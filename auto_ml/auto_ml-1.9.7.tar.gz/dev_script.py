try:
    import cPickle as pickle
except:
    import pickle
import copy
import datetime
import math
import random
import sys
import threading

# import auto_ml.predictor
from auto_ml import Predictor
from auto_ml import utils

from sklearn.metrics import mean_squared_error

if 'fast' in set(sys.argv):
    fast = True
else:
    fast = False

def feature_eng(X):
    for row in X:
        estimate = row.get('direct_r2c_est_duration', 0)
        if estimate is None:
            row['is_long_r2c_est'] = 0
        elif row.get('direct_r2c_est_duration', 0) > 800:
            row['is_long_r2c_est'] = 1
        else:
            row['is_long_r2c_est'] = 0
    return X


if __name__ == '__main__':

    validation_start_date = datetime.datetime(2016, 8, 1)
    # Helper function to write a new set of data_dev
    def write_data_dev_to_file(all_rows, threshold=0.99):
        # Keep more of the validation data (min of some multiple of what we're keeping for dev, or all)
        threshold = float(threshold)
        validation_data_threshold = float(1 - min((1 - threshold) * 3, 1))
        print('threshold')
        print(threshold)
        data_dev = []
        for row in all_rows:
            if row['created_at_in_local_time'] > validation_start_date and random.random() > validation_data_threshold:
                data_dev.append(row)
            elif random.random() > threshold:
                data_dev.append(row)

        with open('data_dev' + str(threshold) + '.pkl', 'wb') as write_file:
            pickle.dump(data_dev, write_file, protocol=pickle.HIGHEST_PROTOCOL)

        print('Successfullly wrote data_dev to file at ' + 'data_dev' + str(threshold) + '.pkl')
        print('len(data_dev):')
        print(len(data_dev))

        # Return the shortened data_dev, and immediately run it through the rest of our process!
        return data_dev

    # saving here so autocomplete works :)
    col_names = ['created_at_in_local_time', 'max_20_percentile_item_prep_time', 'max_20_percentile_category_prep_time', 'avg_median_item_prep_time', 'avg_median_category_prep_time', 'max_80_percentile_item_prep_time', 'max_80_percentile_category_prep_time', 'subtotal', 'total_items_in_order', 'max_original_item_price', 'avg_original_item_price', 'min_original_item_price', 'count_large_items_in_order', 'count_small_items_in_order', 'avg_num_orders_item_appearing_in', 'avg_num_orders_category_appearing_in', 'num_items_with_low_prev_order_count', 'num_categories_with_low_prev_order_count', 'store_starting_point_id', 'market_id', 'submarket_id', 'district_id', 'store_starting_point_id', 'price_range', 'composite_score', 'is_partner', 'rest_price_range', 'restaurant_order_place_latency', 'restaurant_avg_prep_time', 'count_orders_over_100_subtotal', 'restaurant_total_orders', 'rest_avg_rest_order_place_latency_large_orders', 'rest_avg_rest_prep_time_large_orders', 'rest_rest_order_place_latency_lunch_rush_hour', 'rest_rest_order_place_latency_dinner_rush_hour', 'rest_rest_prep_time_lunch_rush_hour', 'rest_rest_prep_time_dinner_rush_hour', 'rest_avg_r2c', 'rest_avg_r2c_vs_estimates', 'rest_avg_r2c_estimates', 'is_automated', 'order_protocol_fax', 'order_protocol_dasher_place', 'order_protocol_phone', 'order_protocol_ipad', 'order_protocol_online_order', 'order_protocol_email', 'preference_level', 'direct_r2c_est_duration', 'flf', 'avg_sp_r2c_estimates', 'sp_avg_r2c', 'sp_avg_r2c_vs_estimates', 'avg_sm_r2c_estimates', 'sm_avg_r2c', 'sm_avg_r2c_vs_estimates', 'avg_district_r2c_estimates', 'district_avg_r2c', 'district_avg_r2c_vs_estimates', 'subpredictor_y_confirmation_latency', 'subpredictor_y_assignment_latency', 'subpredictor_y_has_dasher_unassign', 'rest_avg_ass_lat', 'rest_avg_conf_lat', 'rest_avg_count_dasher_unassigns', 'sm_avg_ass_lat', 'sm_avg_conf_lat', 'sm_avg_count_dasher_unassigns', 'sp_avg_ass_lat', 'sp_avg_conf_lat', 'sp_avg_count_dasher_unassigns', 'district_avg_ass_lat', 'district_avg_conf_lat', 'district_avg_count_dasher_unassigns', 'y_actual_delivery_duration', 'subpredictor_y_order_place_duration', 'subpredictor_y_prep_time_duration', 'current_system_estimated_store_prep_duration', 'current_system_estimated_delivery_duration', 'subpredictor_y_estimated_prep_is_way_off', 'subpredictor_y_estimated_eta_is_way_off', 'subpredictor_y_r2c_duration', 'subpredictor_y_dasher_wait_duration', 'y_current_estimated_delivery_duration']

    props_to_delete = [


        # 'subpredictor_y_prep_time_duration',
        # 'subpredictor_y_order_place_duration',
        'subpredictor_y_order_placer_escalated',
        # 'subpredictor_y_estimated_prep_is_way_off',
        # 'subpredictor_y_estimated_eta_is_way_off',

        'subpredictor_y_refund_was_issued'
        , 'y_current_calculated_estimated_delivery_duration'
        , 'y_current_calculated_estimated_delivery_duration'
        , 'y_current_estimated_delivery_duration'
        , 'is_automated'
    ]


    deleted_features = [
    # Order cart/delivery level features
    'avg_num_orders_item_appearing_in'
    , 'avg_num_orders_category_appearing_in'
    , 'num_items_with_low_prev_order_count'
    , 'num_categories_with_low_prev_order_count'

    # Item Level Features
    , 'max_20_percentile_item_prep_time'
    , 'avg_median_item_prep_time'
    , 'avg_median_category_prep_time'
    , 'max_80_percentile_item_prep_time'
    # Category Level Features
    , 'max_20_percentile_category_prep_time'
    , 'max_80_percentile_category_prep_time'
    # Store Level Features
    , 'price_range'
    # , 'composite_score'
    # , 'is_partner'
    # , 'rest_price_range'
    # , 'restaurant_order_place_latency'
    , 'restaurant_avg_prep_time'
    , 'count_orders_over_100_subtotal'
    , 'restaurant_total_orders'
    # , 'rest_avg_rest_order_place_latency_large_orders'
    , 'rest_avg_rest_prep_time_large_orders'
    , 'rest_rest_order_place_latency_lunch_rush_hour'
    # , 'rest_rest_order_place_latency_dinner_rush_hour'
    , 'rest_rest_prep_time_lunch_rush_hour'
    , 'rest_rest_prep_time_dinner_rush_hour'
    # , 'rest_avg_r2c'
    , 'rest_avg_r2c_vs_estimates'
    , 'rest_avg_r2c_estimates'
    , 'rest_avg_ass_lat'
    , 'rest_avg_conf_lat'
    , 'rest_avg_count_dasher_unassigns'
    # Starting Point Level Features
    # , 'flf'
    , 'avg_sp_r2c_estimates'
    , 'sp_avg_r2c'
    , 'sp_avg_r2c_vs_estimates'
    , 'sp_avg_ass_lat'
    , 'sp_avg_conf_lat'
    , 'sp_avg_count_dasher_unassigns'
    # Submarket Level Features
    # , 'avg_sm_r2c_estimates'
    # , 'sm_avg_r2c'
    # , 'sm_avg_r2c_vs_estimates'
    # TODO: Preston
    # , 'sm_avg_ass_lat'
    , 'sm_avg_conf_lat'
    , 'sm_avg_count_dasher_unassigns'
    # District Level Features
    , 'avg_district_r2c_estimates'
    , 'district_avg_r2c'
    , 'district_avg_r2c_vs_estimates'
    , 'district_avg_ass_lat'
    , 'district_avg_conf_lat'
    , 'district_avg_count_dasher_unassigns'
    # DR Features
    # , 'current_system_estimated_store_prep_duration'
    # , 'current_system_estimated_delivery_duration'
    # misc features
    # , 'store_starting_point_id'
    # , 'market_id'
    # , 'submarket_id'
    # , 'district_id'
    # , 'store_starting_point_id'




    # # Targets
    # 'subpredictor_y_confirmation_latency'
    # 'subpredictor_y_assignment_latency'
    # 'subpredictor_y_has_dasher_unassign'
    # 'y_actual_delivery_duration'
    # 'subpredictor_y_order_place_duration'
    # 'subpredictor_y_prep_time_duration'
    # 'subpredictor_y_estimated_prep_is_way_off'
    # 'subpredictor_y_estimated_eta_is_way_off'
    # 'subpredictor_y_r2c_duration'
    # 'subpredictor_y_dasher_wait_duration'
    # 'y_current_estimated_delivery_duration'

    ]

    props_to_delete = props_to_delete + deleted_features

    if fast:
        props_to_delete.append('subpredictor_y_has_dasher_unassign')
        props_to_delete.append('subpredictor_y_order_place_duration')
        props_to_delete.append('subpredictor_y_dasher_wait_duration')
        props_to_delete.append('subpredictor_y_estimated_eta_is_way_off')
        props_to_delete.append('subpredictor_y_estimated_prep_is_way_off')
        props_to_delete.append('subpredictor_y_assignment_latency')
        props_to_delete.append('subpredictor_y_confirmation_latency')



    # props_to_delete = ['y_current_estimated_delivery_duration', 'y_current_calculated_estimated_delivery_duration']

    # Helper function to delete property names from a row of data
    def delete_prop_names(row, props_to_delete):
        for prop in props_to_delete:
            try:
                del row[prop]
            except:
                pass
        return row


    def calculate_rmse(preds, actuals):
        rmse = mean_squared_error(actuals, preds)**0.5
        return rmse


    # Helper function to remove certain "columns" from our dataset.
    # This allows us to pass in the predicted values from our current model in the input, and then compare how our new model is doing compared to what's currently live.
    def split_output(X, output_column_name):
        y = []
        for row in X:
            y.append(
                row.pop(output_column_name)
            )

        return X, y


    # Default Values
    file_to_load = 'data_dev0.995.pkl'
    write_data_dev = False

    # Figure out which file to load, and if we want to create a new dev dataset
    if len(sys.argv) > 1:
        if sys.argv[1] in set(['write_file', 'shorten', 'shorten_data','make_dev_data', 'make_data_dev']):
            file_to_load = 'data_all.pkl'
            write_data_dev = True
            if len(sys.argv) > 2:
                threshold = sys.argv[2]
            else:
                threshold = 0.995
        elif sys.argv[1] in set(['full', 'long', 'full_dataset', 'all_data', 'all']):
            file_to_load = 'data_all.pkl'
        elif sys.argv[1] in set(['small', '90', '10']):
            file_to_load = 'data_dev0.9.pkl'
        elif sys.argv[1] in set(['medium', '50', 'half']):
            file_to_load = 'data_dev0.5.pkl'
        else:
            # allow the user to use their own thresholds (like 0.95)
            file_to_load = 'data_dev' + sys.argv[1] + '.pkl'

    # This column holds our y values
    target_col = 'y_actual_delivery_duration'
    current_target_col = 'y_current_estimated_delivery_duration'
    bad_vals = set([None, float('nan'), float('Inf')])
    max_target_col_threshold = 120 * 60
    min_target_col_threshold = 5 * 60
    max_subpredictor_y_prep_time_duration_threshold = 120 * 60
    min_subpredictor_y_prep_time_duration_threshold = 2 * 60

    refund_issued_vals = []
    escalated_vals = []

    # Load our data
    with open(file_to_load, 'rb') as read_file:
        all_rows = pickle.load(read_file)
        print('\n\nLoaded the data in file: ' + file_to_load)

        if write_data_dev:
            all_rows = write_data_dev_to_file(all_rows, threshold)

        # Split data into train and test
        training_data = []
        testing_data = []
        testing_data_bad = []
        training_data_bad = []

        y_current_estimated_delivery_duration = []
        # y_current_calculated_estimated_delivery_duration = []

        y_current_estimated_delivery_duration_bad = []
        # y_current_calculated_estimated_delivery_duration_bad = []

        for row in all_rows:


            # Make sure we only include vals that are relevant.
            if row[target_col] not in bad_vals and row[current_target_col] not in bad_vals and row['subpredictor_y_prep_time_duration'] not in bad_vals:

                if not fast:
                    # Feature Engineering for some of the subpredictors we want to train
                    # Mostly, computing the y-values for the subpredictors we want to train
                    if row['y_actual_delivery_duration'] > 60 * 60:
                        row['subpredictor_y_is_over_60_min_deliv_duration'] = 1
                    else:
                        row['subpredictor_y_is_over_60_min_deliv_duration'] = 0

                    if row['y_actual_delivery_duration'] > 90 * 60:
                        row['subpredictor_y_is_over_90_min_deliv_duration'] = 1
                    else:
                        row['subpredictor_y_is_over_90_min_deliv_duration'] = 0


                # Make sure we've got clean data to train on
                if min_target_col_threshold <= row[target_col] <= max_target_col_threshold and min_subpredictor_y_prep_time_duration_threshold <= row['subpredictor_y_prep_time_duration'] <= max_subpredictor_y_prep_time_duration_threshold:

                    # refund_issued_vals.append(row['subpredictor_y_refund_was_issued'])
                    # refund_issued_vals.append(row['subpredictor_y_order_placer_escalated'])

                    # Test Data
                    if row['created_at_in_local_time'] > validation_start_date:

                            # Grab current prediction values to compare against
                            # y_current_calculated_estimated_delivery_duration.append(row.pop('y_current_calculated_estimated_delivery_duration'))
                            y_current_estimated_delivery_duration.append(row.pop('y_current_estimated_delivery_duration'))

                            row = delete_prop_names(row, props_to_delete)
                            testing_data.append(row)

                    # Training Data
                    else:
                        # Clean row of all vals that might induce overfitting (this includes the current estimator's predicted vals that we might want to benchmark against)
                        row = delete_prop_names(row, props_to_delete)
                        training_data.append(row)

                else:
                    y_current_estimated_delivery_duration_bad.append(row.pop('y_current_estimated_delivery_duration', None))

                    row = delete_prop_names(row, props_to_delete)
                    testing_data_bad.append(row)


    print('We have loaded, split, and cleaned the raw data! Here\'s the first item in the dataset to show you an example.')
    print(training_data[0])

    # split out out output column so we have a proper X, y dataset
    X_test, y_test = split_output(testing_data, target_col)
    X_test_bad, y_test_bad = split_output(testing_data_bad, target_col)

    # X_test = testing_data
    # y_test_log = [math.log(val) for val in y_test]
    # y_current_calculated_estimated_delivery_duration_log = [math.log(val) for val in y_current_calculated_estimated_delivery_duration]
    # y_current_estimated_delivery_duration_log = [math.log(val) for val in y_current_estimated_delivery_duration]
    # print('RMSE of ' + 'y_current_calculated_estimated_delivery_duration expressed in natural logs')
    # print(calculate_rmse(y_current_calculated_estimated_delivery_duration_log, y_test_log))
    # print('RMSE of ' + 'y_current_calculated_estimated_delivery_duration in their full scale')
    # print(calculate_rmse(y_current_calculated_estimated_delivery_duration, y_test))
    # print('RMSE of ' + 'y_current_estimated_delivery_duration expressed in natural logs')
    # print(calculate_rmse(y_current_estimated_delivery_duration_log, y_test_log))
    # print('RMSE of ' + 'y_current_estimated_delivery_duration in their full scale')
    # print(calculate_rmse(y_current_estimated_delivery_duration, y_test))
    print('Here is our current system\'s RMSE on the holdout data')
    print(calculate_rmse(y_current_estimated_delivery_duration, y_test))

    print('Here is our current system\'s RMSE on the holdout data including a bunch of bad/outlier values:')
    print(calculate_rmse(y_current_estimated_delivery_duration + y_current_estimated_delivery_duration_bad, y_test + y_test_bad))

    # print('subpredictor_y_refund_was_issued')
    # print(refund_issued_vals)
    # print('subpredictor_y_order_placer_escalated')
    # print(escalated_vals)


    # GET conflat from Jessica. Confirmation Latency. build that in as a subpredictor.
    # Recent deliveries that are comparable
    # Subpredictor for teh number of delivery events (communications between dasher and customer)
    # Batch rates, and triple batch rates. asslat as well. supply generally.
    #


    column_descriptions_hash = {
        'y_actual_delivery_duration': 'output',
        'created_at_in_local_time': 'date',
        'store_starting_point_id': 'categorical',
        'market_id': 'categorical',
        'submarket_id': 'categorical',
        'district_id': 'categorical'
        , 'subpredictor_y_prep_time_duration': 'regressor'
        , 'subpredictor_y_order_place_duration': 'regressor'
        , 'subpredictor_y_r2c_duration': 'regressor'
        , 'subpredictor_y_dasher_wait_duration': 'regressor'

        , 'subpredictor_y_is_over_60_min_deliv_duration': 'classifier'
        , 'subpredictor_y_is_over_90_min_deliv_duration': 'classifier'
        , 'subpredictor_y_estimated_prep_is_way_off': 'classifier'
        , 'subpredictor_y_estimated_eta_is_way_off': 'classifier'

        , 'subpredictor_y_confirmation_latency': 'regressor'
        , 'subpredictor_y_assignment_latency': 'regressor'
        , 'subpredictor_y_has_dasher_unassign': 'classifier'
    }

    if fast:
        try:
            column_descriptions_hash.pop('subpredictor_y_has_dasher_unassign')
            column_descriptions_hash.pop('subpredictor_y_order_place_duration')
            column_descriptions_hash.pop('subpredictor_y_dasher_wait_duration')
            column_descriptions_hash.pop('subpredictor_y_estimated_eta_is_way_off')
            column_descriptions_hash.pop('subpredictor_y_estimated_prep_is_way_off')
            column_descriptions_hash.pop('subpredictor_y_is_over_90_min_deliv_duration')
            column_descriptions_hash.pop('subpredictor_y_is_over_60_min_deliv_duration')
            column_descriptions_hash.pop('subpredictor_y_assignment_latency')
            column_descriptions_hash.pop('subpredictor_y_confirmation_latency')
        except:
            pass

    ml_predictor = Predictor(
        type_of_estimator='regressor',
        column_descriptions=column_descriptions_hash
    )

    print('************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************')

    # ml_predictor.train(training_data, perform_feature_selection=True, X_test=X_test, y_test=y_test, ml_for_analytics=True, compute_power=1, take_log_of_y=False, add_cluster_prediction=False, model_names=['XGBRegressor'], num_weak_estimators=0, user_input_func=feature_eng, optimize_final_model=False)
    ml_predictor.train(training_data, perform_feature_selection=True, ml_for_analytics=True, compute_power=1, take_log_of_y=False, add_cluster_prediction=False, num_weak_estimators=0, optimize_final_model=False, model_names=['GradientBoostingRegressor'])
    # ml_predictor.train(training_data, perform_feature_selection=True, ml_for_analytics=True, compute_power=1, take_log_of_y=False, add_cluster_prediction=False, model_names=['DeepLearningRegressor'], num_weak_estimators=0, optimize_final_model=False)

    trained_model_file_name = ml_predictor.save()
    # print(trained_model_file_name)

    # Load in the saved pipeline
    # with open(trained_model_file_name, "rb") as read_file:
    #     trained_ml_pipeline = pickle.load(read_file)

    trained_ml_pipeline = ml_predictor

    # print('Here is a sample of predictions from our loaded trained_ml_pipeline when given the first 100 items in X_test:')
    # print(trained_ml_pipeline.predict(X_test[:100]))
    print('Here is our score on the holdout data including a bunch of bad/outlier values')
    # print(X_test[:3])
    X_test_all = X_test + X_test_bad
    y_test_all = y_test + y_test_bad

    # X_test_all_copy = copy.deepcopy(X_test_all)
    # y_test_all_copy = copy.deepcopy(y_test_all)


    # print('X_test_all[0] before .score')
    # print(X_test_all[0])

    prediction_start_time = datetime.datetime.now()

    print(trained_ml_pipeline.score(X_test_all, y_test_all))
    prediction_end_time = datetime.datetime.now()

    print('Total prediction time for ' + str(len(X_test_all)) + ' rows all at once:')
    print(prediction_end_time - prediction_start_time)

    # print('X_test_all[0] after .score')
    # print(X_test_all[0])

    prediction_by_row_start_time = datetime.datetime.now()
    for idx, row in enumerate(X_test_all):
        # print('row inside X_test_all_copy')
        # print(row)
        if idx % 100 == 0:
            print(idx)
            print('Total prediction time for doing 100 rows one by one:')

            prediction_by_row_end_time = datetime.datetime.now()
            print(prediction_by_row_end_time - prediction_by_row_start_time)
            prediction_by_row_start_time = prediction_by_row_end_time

        trained_ml_pipeline.predict(row)
        # threading.Thread(target=trained_ml_pipeline.predict, args=row)

    prediction_by_row_end_time = datetime.datetime.now()

    print('Total prediction time for doing each row one by one:')
    print(prediction_by_row_end_time - prediction_by_row_start_time)

    print('Here is our current system\'s RMSE on the holdout data including a bunch of bad/outlier values:')
    print(calculate_rmse(y_current_estimated_delivery_duration + y_current_estimated_delivery_duration_bad, y_test + y_test_bad))

    print('Score on just X_test and y_test')
    print(trained_ml_pipeline.score(X_test, y_test))

    print('Here is our current system\'s RMSE on only these extreme cases:')
    print(calculate_rmse(y_current_estimated_delivery_duration_bad, y_test_bad))
    print('Here is our newly trained predictor\'s performance on only these extreme cases:')
    print(trained_ml_pipeline.score(X_test_bad, y_test_bad))


    # This is all using the trained pipeline that's already in memory
    # print('Here is our score on the holdout data including a bunch of bad/outlier values')
    # # print(X_test[:3])
    # print(ml_predictor.score(X_test + X_test_bad, y_test + y_test_bad))

    # print('Here is our current system\'s RMSE on only these extreme cases:')
    # print(calculate_rmse(y_current_estimated_delivery_duration_bad, y_test_bad))
    # print('Here is our newly trained predictor\'s performance on only these extreme cases:')
    # print(ml_predictor.score(X_test_bad, y_test_bad))


# More Subpredictors:
# Had Issue Associated
# Binary yes/no for is_going_to_be_over_60 minutes
# Binary yes/no for is_going_to_be_over_90 minutes
# train one up on only dasher_place
# Assignment latency
# number of dasher unassigns
# Predict r2c!
# Predict if our current delivery time estimate is going to be way off.
# predict if our current prep time estimate is going to be way off.



# Features
# Restaurant is highly variable
# Restaurant is highly consistent
# number of orders in a submarket
# number of orders in a starting point
# number of orders from restaurant
# maybe restaurant average d2r?
# submarket average d2r?
# Store avg prep time vs. estimates
# store average order place duration?
# time of day average order place duration by store?
# time of day average global order place duration?
# only add in information when appropriate (only add in lunchtime order place duration when it's actually lunchtime)
# store average delivery time
# pull data from all of june, not just two weeks.

# anything to predict subpredictor_y_confirmation_latency_sub_prediction
    # global average by order size
    # restaurant average- probably pretty likely that taco bell has a higher unassign rate than fuki sushi.
    # time of day average
    # district average
    # sm average
    # sp average
    # flf average?


# generally, make more conditional joins.
    # join based on restaurant AND time of day
    # join based on SM AND time of day
    # join based on something AND flf
# This will apply to a bunch of the pre-computed summary stats table
# restaurant prep time by is_lunch_rush_hour should only be joined in if it is lunch rush hour.


# Modeling Improvements
# How we perform feature selection.
# More types of weak estimators
