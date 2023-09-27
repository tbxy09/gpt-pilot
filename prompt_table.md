Here is the output in Markdown format with a table and linked prompts and function calls:

| Call | Prompt | Schema | Functions |
|-|-|-|-| 
| [`self.convo_architecture.send_message('architecture/technologies.prompt', {'name': self.project.args['name'], 'prompt': self.project.project_description, 'user_stories': self.project.user_stories, 'app_type': self.project.args['app_type']}, ARCHITECTURE)`](#ARCHITECTURE) | [`technologies.prompt`](./pilot/prompts/architecture/technologies.prompt) | `{'name': str, 'prompt': str, 'user_stories': list, 'app_type': str}` | [`ARCHITECTURE`](#architecture) |
| [`self.convo_user_stories.send_message('user_stories/specs.prompt', {'name': self.project.args['name'], 'prompt': self.project.project_description, 'app_type': self.project.args['app_type'], 'END_RESPONSE': END_RESPONSE})`](#) | [`specs.prompt`](./pilot/prompts/user_stories/specs.prompt) | `{'name': str, 'prompt': str, 'app_type': str, 'END_RESPONSE': str}` | |
| [`self.convo_project_description.send_message('utils/summary.prompt', {'conversation': conversation_str})`](#) | [`summary.prompt`](./pilot/prompts/utils/summary.prompt) | `{'conversation': str}` | |   
| [`convo.send_message('development/task/next_step.prompt', step_data, EXECUTE_COMMANDS)`](#execute_commands) | [`next_step.prompt`](./pilot/prompts/development/task/next_step.prompt) | `step_data` | [`EXECUTE_COMMANDS`](#execute_commands) |
| [`convo.send_message('development/env_setup/specs.prompt', os_data, FILTER_OS_TECHNOLOGIES)`](#FILTER_OS_TECHNOLOGIES) | [`specs.prompt`](./pilot/prompts/development/env_setup/specs.prompt) | `os_data` | [`FILTER_OS_TECHNOLOGIES`](#FILTER_OS_TECHNOLOGIES) |  
| [`convo.send_message('development/env_setup/install_next_technology.prompt', tech_data)`](#) | [`install_next_technology.prompt`](./pilot/prompts/development/env_setup/install_next_technology.prompt) | `tech_data` | |
| [`convo.send_message('development/env_setup/unsuccessful_installation.prompt', tech_data, EXECUTE_COMMANDS)`](#execute_commands) | [`unsuccessful_installation.prompt`](./pilot/prompts/development/env_setup/unsuccessful_installation.prompt) | `tech_data` | [`EXECUTE_COMMANDS`](#execute_commands) |   
| [`convo.send_message('development/plan.prompt', plan_data, DEVELOPMENT_PLAN)`](#development_plan) | [`plan.prompt`](./pilot/prompts/development/plan.prompt) | `plan_data` | [`DEVELOPMENT_PLAN`](#development_plan) |
| [`convo.send_message('development/task/break_down_code_changes.prompt', code_data)`](#) | [`break_down_code_changes.prompt`](./pilot/prompts/development/task/break_down_code_changes.prompt) | `code_data` | |
| [`convo.send_message('development/task/breakdown.prompt', task_data)`](#) | [`breakdown.prompt`](./pilot/prompts/development/task/breakdown.prompt) | `task_data` | |
| [`convo.send_message('development/task/request_files_for_code_changes.prompt', step_data)`](#) | [`request_files_for_code_changes.prompt`](./pilot/prompts/development/task/request_files_for_code_changes.prompt) | `step_data` | |
| [`convo.send_message('development/implement_changes.prompt', impl_data, IMPLEMENT_CHANGES)`](#implement_changes) | [`implement_changes.prompt`](./pilot/prompts/development/implement_changes.prompt) | `impl_data` | [`IMPLEMENT_CHANGES`](#implement_changes) |  
| [`convo.send_message('development/iteration.prompt', iteration_data)`](#) | [`iteration.prompt`](./pilot/prompts/development/iteration.prompt) | `iteration_data` | |
| [`convo.send_message('development/parse_task.prompt', {}, IMPLEMENT_TASK)`](#implement_task) | [`parse_task.prompt`](./pilot/prompts/development/parse_task.prompt) | `{}` | [`IMPLEMENT_TASK`](#implement_task) |
| [`convo.send_message('development/task/step_check.prompt', {}, GET_TEST_TYPE)`](#get_test_type) | [`step_check.prompt`](./pilot/prompts/development/task/step_check.prompt) | `{}` | [`GET_TEST_TYPE`](#get_test_type) |
| [`convo.send_message('dev_ops/debug.prompt', debug_data, DEBUG_STEPS_BREAKDOWN)`](#debug_steps_breakdown) | [`debug.prompt`](./pilot/prompts/dev_ops/debug.prompt) | `debug_data` | [`DEBUG_STEPS_BREAKDOWN`](#debug_steps_breakdown) |
| [`convo.send_message('dev_ops/ran_command.prompt', cmd_data)`](#./pilot/helpers/cli.py#L214) | [`ran_command.prompt`](./pilot/prompts/dev_ops/ran_command.prompt) | `cmd_data` | |
| [`convo.send_message('dev_ops/should_rerun_command.prompt', cmd)`](#) | [`should_rerun_command.prompt`](./pilot/prompts/dev_ops/should_rerun_command.prompt) | `cmd` | |

<a name="ARCHITECTURE"></a>
##### ARCHITECTURE
[pilot/const/function_calls.py](./pilot/const/function_calls.py#L76)

<a name="FILTER_OS_TECHNOLOGIES"></a>  
##### FILTER_OS_TECHNOLOGIES
[pilot/const/function_calls.py](./pilot/const/function_calls.py#L100)


<a name="EXECUTE_COMMANDS"></a>
##### EXECUTE_COMMANDS   
[pilot/const/function_calls.py](./pilot/const/function_calls.py#L124)

<a name="DEVELOPMENT_PLAN"></a>
##### DEVELOPMENT_PLAN
[pilot/const/function_calls.py](./pilot/pilot/const/function_calls.py#L161)  

<a name="IMPLEMENT_TASK"></a>
##### IMPLEMENT_TASK
[pilot/const/function_calls.py](./pilot/const/function_calls.py#L197)

<a name="IMPLEMENT_CHANGES"></a>
##### IMPLEMENT_CHANGES
[pilot/const/function_calls.py](./pilot/const/function_calls.py#L321)

<a name="GET_TEST_TYPE"></a>
##### GET_TEST_TYPE
[pilot/const/function_calls.py](./pilot/const/function_calls.py#L387)

<a name="DEBUG_STEPS_BREAKDOWN"></a>
##### DEBUG_STEPS_BREAKDOWN
[pilot/const/function_calls.py](./pilot/const/function_calls.py#L441)

Let me know if this formatted output helps or if you need me to clarify or expand on anything!