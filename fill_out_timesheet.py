import timesheet_utils as tu

driver = tu.start_browser(1)

tu.log_in(driver)

tu.click_correct_week_link(driver)

driver = tu.switch_to_timesheet_iframe(driver)

tu.fill_out_hours(driver)

tu.confirm_and_submit(driver)
