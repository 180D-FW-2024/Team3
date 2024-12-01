# imports here, so that this script can call the scripts it needs to
def handle_command(command, recipe_object):
    if(command == "next instruction"):
        recipe_object.nextStep()
    elif(command == "previous instruction"):
        recipe_object.previousStep()
    elif(command == "repeat instruction"):
        recipe_object.currentStep()
    elif(command == "list ingredients"):
        return
    elif(command == "current temperature"):
        return
    elif(command == "time remaining"):
        recipe_object.timeRemaining()
    elif(command == "start timer"):
        recipe_object.startTimer()
    elif(command == "stop timer"):
        recipe_object.stopTimer()
    elif(command == "add ingredient"):
        return
    elif(command == "remove ingredient"):
        return
    elif(command == "recommend recipe"):
        return
    