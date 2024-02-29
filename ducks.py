import typing

from SpiffWorkflow.bpmn.specs.bpmn_process_spec import BpmnProcessSpec
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.camunda.parser.CamundaParser import CamundaParser
from SpiffWorkflow.camunda.specs.user_task import EnumFormField, UserTask
from SpiffWorkflow.task import Task


def show_form(task: Task):
    form = task.task_spec.form

    if task.data is None:
        task.data = {}

    for field in form.fields:
        prompt = field.label
        if isinstance(field, EnumFormField):
            prompt += " (Options: " + ', '.join([str(option.id) for option in field.options]) + ")"
        if field.type == "boolean":
            prompt += " (Options: true, false)"
        prompt += " : "
        answer = input(prompt)
        if field.type == "long":
            answer = int(answer)
        if field.type == "boolean":
            answer = answer.lower().strip()
            answer = (answer == 'true' or answer == 'yes')

        task.update_data({field.id: answer})


parser = CamundaParser()
parser.add_bpmn_file('ducks.bpmn')
spec: BpmnProcessSpec = parser.get_spec('duck_process')
workflow: BpmnWorkflow = BpmnWorkflow(spec)

workflow.do_engine_steps()
ready_tasks: typing.List[Task | None] = workflow.get_ready_user_tasks()
while len(ready_tasks) > 0:
    for task in ready_tasks:
        if isinstance(task.task_spec, UserTask):
            show_form(task)
            print(task.data)
        else:
            print("Complete Task ", task.task_spec.name)
        workflow.run_task_from_id(task.id)
    workflow.do_engine_steps()
    ready_tasks = workflow.get_ready_user_tasks()
print(workflow.last_task.data)
print(workflow)
