import Action
import ActionExecute

ActionList = []

Program = Action.Action

Program.CommandPath = "touch"
Program.Arguments = "test"

ActionList.append(Program)

Runner = ActionExecute.LinearExecuter()

a = Runner.ExecuteActionList(ActionList)

print("Successful: " + str(a))
