def ratio_merge(first_list, second_list, merge_ratio=0.5, desired_length=None, strict=False):
    # This function acts as a generator producing elements from the two given lists by the given <merge_ratio>.
    # The generator would preserve any internal order within the lists and would produce no more then 
    # <desired_length> elements in total.
    # In case the total number of elements withing either the lists is not enough to maintain the desired ratio
    # throughout, the function would continue to generate elements from the remaining set until <desired_length> 
    # elements were produced.
    # If the strict parameter is set to True the function will stop producing elements once one of the lists has
    # ran out of elemets. It whould also bias the produced list to fit closest to the length of the first list.
    current_ratio = 0.0
    current_length = 0
    first_list_pop_count = 0
    second_list_pop_count = 0

    combined_list_length = len(first_list) + len(second_list)
    if desired_length is None or desired_length > combined_list_length:
        desired_length = combined_list_length

    try:
        while current_length < desired_length:
            if current_ratio <= merge_ratio:
                yield first_list[first_list_pop_count]
                first_list_pop_count += 1
            elif not strict or first_list_pop_count < len(first_list):
                yield second_list[second_list_pop_count]
                second_list_pop_count += 1
            current_length += 1
            current_ratio = float(first_list_pop_count) / current_length

    except IndexError:
        if strict:
            return
        lst, lst_count = (first_list, first_list_pop_count) if first_list_pop_count < len(first_list) else (second_list, second_list_pop_count)
        try:
            while current_length < desired_length:
                yield lst[lst_count]
                lst_count += 1
                current_length += 1

        except IndexError:
            return
