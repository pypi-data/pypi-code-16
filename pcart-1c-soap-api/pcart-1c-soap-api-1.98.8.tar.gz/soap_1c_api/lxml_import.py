from ftplib import FTP
from io import BytesIO
from lxml import etree, objectify
from lxml.html import tostring
from urllib.request import Request, urlopen
from django.core.files.storage import default_storage

import pytils
import os
import re
import logging
import traceback

from django.conf import settings
from django.core.files import File
from django.core.files.base import ContentFile
from django.contrib.sites.models import Site
from pcart_catalog.models import (
    Collection,
    ProductType,
    ProductTypeProperty,
    Vendor,
    Product,
    ProductVariant,
    ProductImage,
    ProductStatus)
from .models import (
    XMLFile,
    ProductImportLogMessage,
    ProductTypeRelation,
    ExtraCollectionRelation,
)


logger = logging.getLogger('import1c')


DEFAULT_STATUS_TITLE = 'Нет в наличии'


def import_goods_from_xml(sender, path, task_instance=None):
    """Load a catalog from the XML file
    """
    xml = etree.parse(default_storage.open(path, 'rb'))  # get etree of file

    categories = xml.xpath('Classifier/Category')
    categories_errors = parse_categories(categories, task_instance=task_instance)

    if categories_errors:
        for k, v in categories_errors.items():
            logger.error('%s : %s' % (k, v))

    products = xml.xpath('Catalog/Product')
    products_errors = parse_products(products, task_instance=task_instance)

    if products_errors:
        for k, v in products_errors.items():
            logger.error('%s : %s' % (k, v))
    return products_errors


def get_first_or_empty(obj):
    try:
        return obj[0].text
    except IndexError:
        return ''


def parse_categories(categories, task_instance=None):
    """ Load product types and colelctions from the Classifier/Category
    section from the XML file.
    """
    TOP_CATEGORY = '00000000-0000-0000-0000-000000000000'
    site = Site.objects.get_current()

    errors = {}
    for category_tag in categories:
        uuid = category_tag.get('UUID')
        try:
            published = True

            marked_for_delete = category_tag.get('Marked')
            parent = category_tag.get('Parent')
            title = category_tag.get('Name')

            # Unpublish marked collections
            if marked_for_delete == 'true':
                published = False

            try:
                pt_relation = ProductTypeRelation.objects.get(
                    alternate_uuid=uuid)

                save_collection = False
                save_product_type = False

                _product_type = pt_relation.product_type
                _collection = pt_relation.collection

                if not published and _collection.published is True:
                    _collection.published = published  # Unpublish
                    save_collection = True
                if title != _collection.title:
                    _collection.title = title  # Change Collection title
                    save_collection = True
                if title != _product_type.title:
                    _product_type.title = title  # Change ProductType title
                    save_product_type = True
                if parent == TOP_CATEGORY and _collection.parent is not None:
                    _collection.parent = None  # Move a collection to the top
                    save_collection = True
                if parent != TOP_CATEGORY:
                    try:
                        parent_pt_relation = ProductTypeRelation.objects.get(
                            alternate_uuid=parent)
                        # Change a collection's parent
                        _parent_collection = parent_pt_relation.collection
                        if _collection.parent != _parent_collection:
                            _collection.parent = _parent_collection
                            save_collection = True
                    except ProductTypeRelation.DoesNotExist:
                        errors[uuid] = 'Unknown parent category %s' % parent

                if title != pt_relation.title:
                    pt_relation.title = title
                    pt_relation.save()

                if save_collection:
                    _collection.save()
                if save_product_type:
                    _product_type.save()

            except ProductTypeRelation.DoesNotExist:
                try:
                    product_type = ProductType.objects.get(title=title)
                except ProductType.DoesNotExist:
                    product_type = ProductType.objects.create(title=title)

                try:
                    collection = Collection.objects.get(title=title)
                except Collection.DoesNotExist:
                    collection = Collection(
                        site=site,
                        title=title,
                        slug=get_unique_collection_slug(title),
                        published=published,
                    )
                    if parent != TOP_CATEGORY:
                        try:
                            parent_pt_relation = \
                                ProductTypeRelation.objects.get(
                                    alternate_uuid=parent)
                            # Change a collection's parent
                            collection.parent = parent_pt_relation.collection
                        except ProductTypeRelation.DoesNotExist:
                            errors[uuid] = \
                                'Unknown parent category %s' % parent
                    collection.save()

                pt_relation = ProductTypeRelation(
                    title=title,
                    alternate_uuid=uuid,
                    product_type=product_type,
                    collection=collection,
                )
                pt_relation.save()
        except Exception as e:
            errors[uuid] = '%s' % str(e)

    return errors


def parse_products(products, task_instance=None):
    """ Load products from the Catalog/Product section from the XML file.
    """
    errors = {}

    extra_collection_relations = ExtraCollectionRelation.objects.all()

    if task_instance:
        size = len(products)
        counter = 0

    for product_tag in products:
        if task_instance:
            counter += 1
            task_instance.update_state(
                state='PROGRESS', meta={'progress': int(counter/size*100)})

        uuid = product_tag.get('UUID')
        try:
            published = True
            category = product_tag.get('Parent')

            id_1c = product_tag.get('ID1C').strip()
            marked_for_delete = product_tag.get('Marked')
            title = get_first_or_empty(product_tag.xpath('Name')).strip()
            prices = product_tag.xpath('Prices/Price')

            # Unpublish marked products
            if marked_for_delete == 'true':
                published = False

            # SKU
            try:
                sku = get_first_or_empty(product_tag.xpath('Article'))
            except IndexError:
                sku = ''

            # Vendor
            try:
                vendor = get_first_or_empty(product_tag.xpath('Manufacturer'))
            except IndexError:
                vendor = ''

            # Short description
            # try:
            #     short_description = product_tag.xpath(
            #         u'MetaContent/DescriptionShort')[0].text
            # except IndexError:
            #     short_description = u''

            # Description
            try:
                description = get_first_or_empty(product_tag.xpath(
                    'MetaContent/DescriptionFull'))
            except IndexError:
                description = ''

            # Status
            try:
                status = get_first_or_empty(product_tag.xpath('Status'))
            except IndexError:
                status = DEFAULT_STATUS_TITLE

            # product with variant
            try:
                parent_product = get_first_or_empty(product_tag.xpath(
                    'ParentProduct'))
            except IndexError:
                parent_product = ''

            # sale price of product
            try:
                compare_at_price = product_tag.xpath('Prices/SalePrice')
            except IndexError:
                compare_at_price = None

            # Warranty
            try:
                warranty = get_first_or_empty(product_tag.xpath('Warranty'))
                warranty = int(warranty)
            except:
                warranty = 0

            # IsParent
            try:
                is_parent = get_first_or_empty(product_tag.xpath('IsParent'))
                is_parent = True if is_parent.lower() == 'true' else False
            except:
                is_parent = False

            # Find the item type (product or variant)
            item_type = 'product'
            if is_parent is False and parent_product != '':
                item_type = 'variant'

            # TODO: work with unit
            # unit = product_tag.xpath('/Unit')[0]
            # unit_id = unit.get(u'ID')
            # unit_name = unit.get(u'Name')
            # unit_full_name = unit.get(u'FullName')
            # unit_inter = unit.get(u'International')

            # TODO: check if to use this
            # quantity = product_tag.xpath('Quantity')[0].text

            pictures = product_tag.xpath('Pictures/Picture')

            # Options
            options = product_tag.xpath('Options/Option')

            # Special meta content
            meta_content = product_tag.xpath('MetaContent')

            # Default values
            page_title = meta_description = ''
            extra_collections = []

            if meta_content:
                meta_content = meta_content[0]
                page_title = \
                    get_first_or_empty(meta_content.xpath('METATitle'))
                meta_description = get_first_or_empty(
                    meta_content.xpath('METADescription'))
                # meta_keywords = meta_content.xpath('METAKeywords')

                for ecr in extra_collection_relations:
                    # Check for: Accesories, New, Popular and Recommended
                    t = get_first_or_empty(meta_content.xpath(ecr.tag_name))
                    if t and t.lower() == 'true':
                        extra_collections.append(ecr.collection)

            # print('::', uuid, item_type, is_parent, parent_product)

            if item_type == 'product':
                obj, created = get_or_create_product(
                    id=uuid,
                    title=title,
                    description=description,
                    page_title=page_title,
                    meta_description=meta_description,
                    vendor=vendor,
                    category=category,
                    sku=sku,
                    barcode=id_1c,
                    price=get_product_price(prices),
                    compare_at_price=compare_at_price,
                    published=published,
                    status=status,
                    options=options,
                    extra_collections=extra_collections,
                )
            else:
                obj, created = get_or_create_variant(
                    id=uuid,
                    title=title,
                    parent_product=parent_product,
                    category=category,
                    sku=sku,
                    barcode=id_1c,
                    status=status,
                    price=get_product_price(prices),
                    compare_at_price=compare_at_price,
                    options=options,
                )

            # if product:
            #     ProductImportLog.objects.create(
            #         product=product,
            #         file_link=file_link,
            #         job=job,
            #         text=tostring(product_tag),
            #     )

            # # accessories
            # if created or UPDATE_1C_ACCESSORIES:
            #     try:
            #         accessories = product_tag.xpath(
            #             'Accesories/Accessory')  # TODO: fix "Accesories"
            #         uids = [a.text for a in accessories]
            #         accessories = Product.objects.filter(uid__in=uids)
            #         for acc in accessories:
            #             ProductAccessories.objects.get_or_create(
            #                 product=product, accessory=acc)
            #     except:
            #         pass

            # # recommended products for product
            # if UPDATE_1C_RELATED:
            #     recommendeds = product_tag.xpath(
            #         u'RecommendedProducts/RecommendedProduct')
            #     product.related_products.clear()
            #     for recommended in recommendeds:
            #         r = Product.objects.get(uid=recommended.text)
            #         product.related_products.add(r)

            # Images
            # # from tasks.models import Job

            # pictures_list = []
            # for p in pictures:
            #     pictures_list.append({
            #         'URL': p.get('URL'),
            #         'Name': p.get('Name'),
            #         'Marked': p.get('Marked'),
            #         'Default': p.get('Default'),
            #     })
            # products_images_dict[product.uid] = pictures_list

            # TODO: should think about how to be with images for variants
            if item_type == 'product':
                img_target_obj = obj
            else:
                img_target_obj = obj.product

            update_product_images(img_target_obj, pictures)
            # load_images(product, pictures)

            # # Options
            # if created or UPDATE_1C_OPTIONS:
            #     load_options(product, options, parent)

            # uuids.append(uuid)
            # if 'tetradka' in settings.INSTALLED_APPS:
            #     from tetradka.listeners import product_saved_listener
            #     product_saved_listener(None, product)
        except Exception as e:
            raise e
            # if getattr(settings, 'WRITE_ERRORS_TO_LOG', False):
            logger.error(str(e))
            errors[uuid] = '%s' % str(e)
    # job = Job.objects.create(
    #     name='soap_1c_api.jobs.product_load_images',
    #     duty=1,
    #     status='success'
    # )
    # job.kwargs = products_images_dict
    # job.save()
    # if uids:
    #     mediator.publish(None, 'similar_products:make', uids)
    return errors


def update_product_images(product, pictures):
    pictures_list = []
    for p in pictures:
        pictures_list.append({
            'URL': p.get('URL'),
            'Name': p.get('Name'),
            'Marked': p.get('Marked'),
            'Default': p.get('Default'),
        })

    p_images = product.images.all()
    old_pictures_list = []
    old_links = []
    for im in p_images:
        # Ignore images or snippets which could be added manually
        if im.download_link:
            old_links.append(im.download_link)
            old_pictures_list.append({
                'URL': im.download_link,
                'Name': im.title,
            })

    for p in pictures_list:
        if p['URL'] in old_links:
            if p['Marked'] == 'true':
                # Delete marked image
                product.images.filter(download_link=p['URL']).delete()
                logger.warning(
                    '%s : Image %s has been removed.' % (product.id, p['URL']))
            else:
                p_ims = product.images.filter(download_link=p['URL'])
                p_ims.update(title=p['Name'])
        else:
            # Add new image
            image = ProductImage(
                title=p['Name'] or product.title,
                product=product,
                download_link=p['URL'],
            )
            image.save()
            # Now the signal should raised after saving and
            # the new task for download the file automatically
            # have be started via Celery. Do not worry about that here.


def get_or_create_status(status):
    try:
        result = ProductStatus.objects.get(title=status)
    except:
        result = ProductStatus.objects.create(
            title=status,
            show_buy_button=True,
            is_visible=True,
            is_searchable=True
        )
    return result


def get_or_create_vendor(vendor):
    try:
        result = Vendor.objects.get(title=vendor)
    except Vendor.DoesNotExist:
        result = Vendor.objects.create(title=vendor)
    return result


def get_product_type_and_collection(category):
    try:
        pt_relation = ProductTypeRelation.objects.get(alternate_uuid=category)
        product_type = pt_relation.product_type
        collection = pt_relation.collection
    except ProductTypeRelation.DoesNotExist:
        return None, None
    return product_type, collection


def get_unique_collection_slug(title):
    import itertools
    _slug = _orig = pytils.translit.slugify(title)
    for x in itertools.count(1):
        if not Collection.objects.filter(slug=_slug).exists():
            break
        _slug = '%s-%d' % (_orig, x)
    return _slug


def get_unique_product_slug(title):
    import itertools
    _slug = _orig = pytils.translit.slugify(title)
    for x in itertools.count(1):
        if not Product.objects.filter(slug=_slug).exists():
            break
        _slug = '%s-%d' % (_orig, x)
    return _slug


def get_unique_variant_slug(product_id, title):
    import itertools
    _slug = _orig = pytils.translit.slugify(title)
    for x in itertools.count(1):
        if not ProductVariant.objects.filter(
                product_id=product_id, slug=_slug).exists():
            break
        _slug = '%s-%d' % (_orig, x)
    return _slug


def get_or_create_product(
        id, title, description, page_title, meta_description,
        vendor, category, sku, barcode,
        price, compare_at_price,
        published, status, options,
        extra_collections=[]):
    """ Create or update parent product.
    """

    status_obj = get_or_create_status(status)
    vendor_obj = get_or_create_vendor(vendor)
    product_type, collection = get_product_type_and_collection(category)
    update_product_type_properties(options, category)

    params = {
        'title': title,
        'sku': sku,
        'barcode': barcode,
        'status': status_obj,
        'vendor': vendor_obj,
        'price': price or 0.0,
        'compare_at_price': compare_at_price or 0.0,
        'published': published,
        'properties': get_properties_dict(options),
        'product_type': product_type,
    }

    if getattr(settings, 'UPDATE_1C_SEO_PRODUCTS', True):
        params.update({
            'page_title': page_title,
            'meta_description': meta_description,
        })

    if getattr(settings, 'UPDATE_1C_PRODUCTS_DESCRIPTION', True):
        params.update({
            'description': description,
        })

    create = False
    try:
        product = Product.objects.get(id=id)
        for k, v in params.items():
            setattr(product, k, v)
        product.save()
        if not product.collections.filter(id=collection.id).exists():
            product.collections.add(collection)
    except Product.DoesNotExist:
        params.update({
            'id': id,
            'slug': get_unique_product_slug(title),
        })
        product = Product(**params)
        product.save()
        create = True
        product.collections.add(collection)

    if extra_collections:
        product.collections.add(*extra_collections)

    return product, create


def get_or_create_variant(
        id, title, parent_product,
        category,
        sku, barcode, status,
        price, compare_at_price,
        options):
    """ Create or update variant product.
    """
    status_obj = get_or_create_status(status)
    update_product_type_properties(options, category)

    params = {
        'title': title,
        'sku': sku,
        'barcode': barcode,
        'status': status_obj,
        'product_id': parent_product,
        'price': price or 0.0,
        'compare_ar_price': compare_at_price or 0.0,
        # 'published': published,
        'properties': get_properties_dict(options),
    }
    create = False
    try:
        variant = ProductVariant.objects.get(id=id)
        for k, v in params.items():
            setattr(variant, k, v)
        variant.save()
    except ProductVariant.DoesNotExist:
        params.update({
            'id': id,
            'product_id': parent_product,
            'slug': get_unique_variant_slug(parent_product, title),
        })
        variant = ProductVariant(**params)
        variant.save()
        create = True

    return variant, create


def update_product_type_properties(options, alternate_uuid):
    try:
        pt_relation = ProductTypeRelation.objects.get(
            alternate_uuid=alternate_uuid)
        product_type = pt_relation.product_type

        _properties = [option.get('Name') for option in options]
        for p in _properties:
            try:
                ProductTypeProperty.objects.get(
                    title=p, product_type=product_type)
            except ProductTypeProperty.DoesNotExist:
                ProductTypeProperty.objects.create(
                    title=p, product_type=product_type)
    except ProductTypeRelation.DoesNotExist:
        logger.warning(
            'Product type relation for %s does not exist.' % alternate_uuid)


def get_properties_dict(options):
    _properties = dict()
    for option in options:
        # group_name = option.get('Group')  # do not supported yet
        property_name = option.get('Name')
        property_value = option.get('Value')
        _properties[property_name] = property_value
    return _properties


def get_product_price(prices):
    for price in prices:
        price_for_unit = get_first_or_empty(price.xpath('PriceForUnit'))
        price = float(price_for_unit.replace(',', '.'))
        return price
    return 0.0
