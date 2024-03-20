import copy

def optimize_tree(main_arr, start_with_gamma_id_1=None, start_with_gamma_id_2=None):
    TOTAL_NODES = 31

    final_arr = None

    len_main_arr = len(main_arr)

    for i in range(len_main_arr):
        structured_arr = [{} for _ in range(TOTAL_NODES)]
        structured_arr[0] = main_arr[i]
        gamma1, gamma2 = structured_arr[0]['gamma1'], structured_arr[0]['gamma2']

        if start_with_gamma_id_1 and (gamma1['id'] != start_with_gamma_id_1 or gamma2['id'] == start_with_gamma_id_1):
            gamma1, gamma2 = gamma2, gamma1

        elif start_with_gamma_id_2 and (gamma2['id'] != start_with_gamma_id_2 or gamma1['id'] == start_with_gamma_id_2):
            gamma1, gamma2 = gamma2, gamma1

        temp_arr = structer_data_in_tree(main_arr[:i] + main_arr[i+1:], copy.deepcopy(structured_arr))

        if not final_arr or (start_with_gamma_id_1 and temp_arr[0]['gamma1']['id'] == start_with_gamma_id_1) or (start_with_gamma_id_2 and temp_arr[0]['gamma2']['id'] == start_with_gamma_id_2):
            final_arr = temp_arr

        if final_arr.count(None) == 0 and not (start_with_gamma_id_1 or start_with_gamma_id_2):
            break

        final_arr_count_none = final_arr.count(None)
        temp_arr_count_none = temp_arr.count(None)

        if final_arr_count_none > temp_arr_count_none:
            final_arr = copy.deepcopy(temp_arr)

    return final_arr


def get_full_tree_arr(main_arr, start_with_gamma_id_1=None, start_with_gamma_id_2=None, objective_id=None):
    final_arr = None

    # Checking the max full binary tree, for every element in array forming the Binary tree.
    len_main_arr = len(main_arr)
    for i in range(len_main_arr):
        # Defining empty array
        structured_arr = [{} for _ in range((TOTAL_NODES))]

        # Assigning Root Node
        structured_arr[0] = (main_arr[i])
        structured_arr_0_gamma1 = structured_arr[0]['gamma1']
        structured_arr_0_gamma2 = structured_arr[0]['gamma2']
        gammaIdGiven = False
        if start_with_gamma_id_1:
            if structured_arr_0_gamma1['id'] != start_with_gamma_id_1 or structured_arr_0_gamma2['id'] == start_with_gamma_id_1:
                structured_arr_0_gamma1, structured_arr_0_gamma2 = structured_arr_0_gamma2, structured_arr_0_gamma1
                gammaIdGiven = True
        elif start_with_gamma_id_2:
            if structured_arr_0_gamma2['id'] != start_with_gamma_id_2 or structured_arr_0_gamma1['id'] == start_with_gamma_id_2:
                structured_arr_0_gamma1, structured_arr_0_gamma2 = structured_arr_0_gamma2, structured_arr_0_gamma1
                gammaIdGiven = True

        temp_arr = structer_data_in_tree(
            main_arr[:i] + main_arr[i+1:], copy.deepcopy(structured_arr))

        if not final_arr:
            final_arr = copy.deepcopy(temp_arr)

        # updating the final tree with Specific Gamma Id positions
        elif start_with_gamma_id_1:
            if final_arr[0]['gamma1']['id'] != start_with_gamma_id_1 and temp_arr[0]['gamma1']['id'] == start_with_gamma_id_1:
                # if final_arr[0]['objective']['id'] != objective_id or temp_arr[0]['objective']['id'] == objective_id:
                final_arr = temp_arr
                gammaIdGiven = False

        elif start_with_gamma_id_2:
            if final_arr[0]['gamma2']['id'] != start_with_gamma_id_2 and temp_arr[0]['gamma2']['id'] == start_with_gamma_id_2:
                # if final_arr[0]['objective']['id'] != objective_id or temp_arr[0]['objective']['id'] == objective_id:
                final_arr = temp_arr
                gammaIdGiven = False

        if final_arr.count(None) == 0 and not gammaIdGiven:
            break
        # Calculating the minimum None value in array. Minimum None value means the near to full binary tree.
        final_arr_count_none = final_arr.count(None)
        temp_arr_count_none = temp_arr.count(None)
        if final_arr_count_none > temp_arr_count_none:
            if (start_with_gamma_id_1 and temp_arr[0]['gamma1']['id'] == start_with_gamma_id_1) or (start_with_gamma_id_2 and temp_arr[0]['gamma2']['id'] == start_with_gamma_id_2) or (not start_with_gamma_id_1 and not start_with_gamma_id_2):
                    # if final_arr[0]['objective']['id'] != objective_id or temp_arr[0]['objective']['id'] == objective_id:
                    final_arr = copy.deepcopy(temp_arr)

    return final_arr
