from prompt_toolkit.shortcuts import create_confirm_application, run_application

def confirm_without_ctrl_c(message):
    app = create_confirm_application(message)
    return run_application(app)