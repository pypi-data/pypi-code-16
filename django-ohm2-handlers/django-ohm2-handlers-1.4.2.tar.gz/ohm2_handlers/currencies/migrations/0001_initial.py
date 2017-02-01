# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-06 19:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ConvertionRate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identity', models.CharField(max_length=2048, unique=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_update', models.DateTimeField(default=django.utils.timezone.now)),
                ('source', models.CharField(max_length=2048)),
                ('rate', models.FloatField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identity', models.CharField(max_length=2048, unique=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_update', models.DateTimeField(default=django.utils.timezone.now)),
                ('code', models.CharField(choices=[('XUA', 'ADB Unit of Account'), ('AFN', 'Afghani'), ('DZD', 'Algerian Dinar'), ('ARS', 'Argentine Peso'), ('AMD', 'Armenian Dram'), ('AWG', 'Aruban Florin'), ('AUD', 'Australian Dollar'), ('AZN', 'Azerbaijanian Manat'), ('BSD', 'Bahamian Dollar'), ('BHD', 'Bahraini Dinar'), ('THB', 'Baht'), ('PAB', 'Balboa'), ('BBD', 'Barbados Dollar'), ('BYR', 'Belarusian Ruble'), ('BZD', 'Belize Dollar'), ('BMD', 'Bermudian Dollar'), ('BOB', 'Boliviano'), ('VEF', 'Bolívar'), ('XBA', 'Bond Markets Unit European Composite Unit (EURCO)'), ('XBB', 'Bond Markets Unit European Monetary Unit (E.M.U.-6)'), ('XBD', 'Bond Markets Unit European Unit of Account 17 (E.U.A.-17)'), ('XBC', 'Bond Markets Unit European Unit of Account 9 (E.U.A.-9)'), ('BRL', 'Brazilian Real'), ('BND', 'Brunei Dollar'), ('BGN', 'Bulgarian Lev'), ('BIF', 'Burundi Franc'), ('XOF', 'CFA Franc BCEAO'), ('XAF', 'CFA Franc BEAC'), ('XPF', 'CFP Franc'), ('CVE', 'Cabo Verde Escudo'), ('CAD', 'Canadian Dollar'), ('KYD', 'Cayman Islands Dollar'), ('CLP', 'Chilean Peso'), ('XTS', 'Codes specifically reserved for testing purposes'), ('COP', 'Colombian Peso'), ('KMF', 'Comoro Franc'), ('CDF', 'Congolese Franc'), ('BAM', 'Convertible Mark'), ('NIO', 'Cordoba Oro'), ('CRC', 'Costa Rican Colon'), ('CUP', 'Cuban Peso'), ('CZK', 'Czech Koruna'), ('GMD', 'Dalasi'), ('DKK', 'Danish Krone'), ('MKD', 'Denar'), ('DJF', 'Djibouti Franc'), ('STD', 'Dobra'), ('DOP', 'Dominican Peso'), ('VND', 'Dong'), ('XCD', 'East Caribbean Dollar'), ('EGP', 'Egyptian Pound'), ('SVC', 'El Salvador Colon'), ('ETB', 'Ethiopian Birr'), ('EUR', 'Euro'), ('FKP', 'Falkland Islands Pound'), ('FJD', 'Fiji Dollar'), ('HUF', 'Forint'), ('GHS', 'Ghana Cedi'), ('GIP', 'Gibraltar Pound'), ('XAU', 'Gold'), ('HTG', 'Gourde'), ('PYG', 'Guarani'), ('GNF', 'Guinea Franc'), ('GYD', 'Guyana Dollar'), ('HKD', 'Hong Kong Dollar'), ('UAH', 'Hryvnia'), ('ISK', 'Iceland Krona'), ('INR', 'Indian Rupee'), ('IRR', 'Iranian Rial'), ('IQD', 'Iraqi Dinar'), ('JMD', 'Jamaican Dollar'), ('JOD', 'Jordanian Dinar'), ('KES', 'Kenyan Shilling'), ('PGK', 'Kina'), ('LAK', 'Kip'), ('HRK', 'Kuna'), ('KWD', 'Kuwaiti Dinar'), ('AOA', 'Kwanza'), ('MMK', 'Kyat'), ('GEL', 'Lari'), ('LBP', 'Lebanese Pound'), ('ALL', 'Lek'), ('HNL', 'Lempira'), ('SLL', 'Leone'), ('LRD', 'Liberian Dollar'), ('LYD', 'Libyan Dinar'), ('SZL', 'Lilangeni'), ('LSL', 'Loti'), ('MGA', 'Malagasy Ariary'), ('MWK', 'Malawi Kwacha'), ('MYR', 'Malaysian Ringgit'), ('MUR', 'Mauritius Rupee'), ('MXN', 'Mexican Peso'), ('MDL', 'Moldovan Leu'), ('MAD', 'Moroccan Dirham'), ('MZN', 'Mozambique Metical'), ('NGN', 'Naira'), ('ERN', 'Nakfa'), ('NAD', 'Namibia Dollar'), ('NPR', 'Nepalese Rupee'), ('ANG', 'Netherlands Antillean Guilder'), ('ILS', 'New Israeli Sheqel'), ('TWD', 'New Taiwan Dollar'), ('NZD', 'New Zealand Dollar'), ('BTN', 'Ngultrum'), ('KPW', 'North Korean Won'), ('NOK', 'Norwegian Krone'), ('MRO', 'Ouguiya'), ('PKR', 'Pakistan Rupee'), ('XPD', 'Palladium'), ('MOP', 'Pataca'), ('TOP', 'Pa’anga'), ('CUC', 'Peso Convertible'), ('UYU', 'Peso Uruguayo'), ('PHP', 'Philippine Peso'), ('XPT', 'Platinum'), ('GBP', 'Pound Sterling'), ('BWP', 'Pula'), ('QAR', 'Qatari Rial'), ('GTQ', 'Quetzal'), ('ZAR', 'Rand'), ('OMR', 'Rial Omani'), ('KHR', 'Riel'), ('RON', 'Romanian Leu'), ('MVR', 'Rufiyaa'), ('IDR', 'Rupiah'), ('RUB', 'Russian Ruble'), ('RWF', 'Rwanda Franc'), ('XDR', 'SDR (Special Drawing Right)'), ('SHP', 'Saint Helena Pound'), ('SAR', 'Saudi Riyal'), ('RSD', 'Serbian Dinar'), ('SCR', 'Seychelles Rupee'), ('XAG', 'Silver'), ('SGD', 'Singapore Dollar'), ('PEN', 'Sol'), ('SBD', 'Solomon Islands Dollar'), ('KGS', 'Som'), ('SOS', 'Somali Shilling'), ('TJS', 'Somoni'), ('SSP', 'South Sudanese Pound'), ('LKR', 'Sri Lanka Rupee'), ('XSU', 'Sucre'), ('SDG', 'Sudanese Pound'), ('SRD', 'Surinam Dollar'), ('SEK', 'Swedish Krona'), ('CHF', 'Swiss Franc'), ('SYP', 'Syrian Pound'), ('BDT', 'Taka'), ('WST', 'Tala'), ('TZS', 'Tanzanian Shilling'), ('KZT', 'Tenge'), ('XXX', 'The codes assigned for transactions where no currency is involved'), ('TTD', 'Trinidad and Tobago Dollar'), ('MNT', 'Tugrik'), ('TND', 'Tunisian Dinar'), ('TRY', 'Turkish Lira'), ('TMT', 'Turkmenistan New Manat'), ('AED', 'UAE Dirham'), ('USD', 'US Dollar'), ('UGX', 'Uganda Shilling'), ('UZS', 'Uzbekistan Sum'), ('VUV', 'Vatu'), ('KRW', 'Won'), ('YER', 'Yemeni Rial'), ('JPY', 'Yen'), ('CNY', 'Yuan Renminbi'), ('ZMW', 'Zambian Kwacha'), ('ZWL', 'Zimbabwe Dollar'), ('PLN', 'Zloty')], max_length=64)),
                ('name', models.CharField(max_length=2048)),
                ('symbol', models.CharField(max_length=64)),
                ('decimals', models.PositiveIntegerField()),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='LastConvertionRate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identity', models.CharField(max_length=2048, unique=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_update', models.DateTimeField(default=django.utils.timezone.now)),
                ('convertion_rate', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='currencies.ConvertionRate')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='convertionrate',
            name='input',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='input_currency', to='currencies.Currency'),
        ),
        migrations.AddField(
            model_name='convertionrate',
            name='output',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='output_currency', to='currencies.Currency'),
        ),
    ]
