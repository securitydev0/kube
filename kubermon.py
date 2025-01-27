import subprocess
import sys
import pyfiglet
import inquirer
import os
from termcolor import colored


def run_kubectl_command(command):
    """Function to execute kubectl commands."""
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        sys.exit(1)


def show_commands():
    """Function to display the list of available commands."""
    commands = [
        "get-nodes",
        "get-contexts",
        "select-context",
        "list-namespaces",
        "not-running-pods",
        "delete-pods",
        "list-deployments",
        "check-deployment-status",
        "cordon-nodes",
        "list-pods",
        "list-pods-on-nodes",
        "image-version",
        "restart-deployment",
        "check-crash-log",
        "events",
        "all-events",
        "list-pod-with-labels",
        "list-containers",
        "container-logs",
        "deploy-logs",
        "services-logs"
    ]
    return commands


def clear_screen():
    """Clear the terminal screen."""
    os.system("clear")  # On Linux/MacOS
    # os.system("cls")  # On Windows

def get_contexts():
    contexts = run_kubectl_command("kubectl config get-contexts")
    lines = contexts.splitlines()

    for line in lines:
        if '*' in line:
            print(colored(line, 'green'))
        else:
            print(line)

def select_context():
    """Function to select and switch to a Kubernetes context."""
    contexts = run_kubectl_command("kubectl config get-contexts -o name").splitlines()
    if not contexts:
        print("No contexts found.")
        return

    questions = [
        inquirer.List(
            "context",
            message="Select a Kubernetes context:",
            choices=contexts,
            carousel=True
        ),
    ]

    answers = inquirer.prompt(questions)
    if answers is None:
        print("No context selected.")
        return

    selected_context = answers.get('context')
    if selected_context:
        print(f"Switching to context: {selected_context}")
        switch_command = f"kubectl config use-context {selected_context}"
        result = run_kubectl_command(switch_command)
        print(f"{result} DONE...")
    else:
        print("No context selected.")

def list_not_running_pods():
    """Function to list all pods not in the Running state in a specific namespace."""
    namespaces = run_kubectl_command("kubectl get ns --no-headers -o custom-columns=:metadata.name").splitlines()
    if not namespaces:
        print("No namespaces found.")
        return

    questions = [
        inquirer.List(
            "namespace",
            message="Select a Kubernetes namespace:",
            choices=namespaces,
            carousel=True
        ),
    ]
    answers = inquirer.prompt(questions)
    if answers is None:
        print("No namespace selected.")
        return

    selected_namespace = answers.get('namespace')
    if selected_namespace:
        print(f"Listing pods not in the Running state in namespace: {selected_namespace}")
        pods_command = f"kubectl get pods -n {selected_namespace} --field-selector=status.phase!=Running"
        pods_output = run_kubectl_command(pods_command)
        print(pods_output)
    else:
        print("No namespace selected.")

def delete_pods():
    """Function to delete pods not in the Running state in a selected namespace."""
    namespaces = run_kubectl_command("kubectl get ns --no-headers -o custom-columns=:metadata.name").splitlines()
    if not namespaces:
        print("No namespaces found.")
        return

    questions = [
        inquirer.List(
            "namespace",
            message="Select a Kubernetes namespace to delete pods not in Running state:",
            choices=namespaces,
            carousel=True
        ),
    ]
    answers = inquirer.prompt(questions)
    if answers is None:
        print("No namespace selected.")
        return

    selected_namespace = answers.get('namespace')
    if selected_namespace:
        print(f"Deleting pods not in the Running state in namespace: {selected_namespace}")
        delete_command = f"kubectl delete pods --namespace {selected_namespace} --field-selector=status.phase!=Running --grace-period=0 --force"
        delete_output = run_kubectl_command(delete_command)
        if delete_output != "No resources found":
            print("Deletion complete.")
            print(delete_output)
        print(delete_output)
    else:
        print("No namespace selected.")

def list_deployments():
    """Function to list deployments in a specific namespace."""
    namespaces = run_kubectl_command("kubectl get ns --no-headers -o custom-columns=:metadata.name").splitlines()
    if not namespaces:
        print("No namespaces found.")
        return

    questions = [
        inquirer.List(
            "namespace",
            message="Select a Kubernetes namespace to list deployments:",
            choices=namespaces,
            carousel=True
        ),
    ]

    answers = inquirer.prompt(questions)
    if answers is None:
        print("No namespace selected.")
        return

    selected_namespace = answers.get('namespace')
    if selected_namespace:
        print(f"Listing deployments in namespace: {selected_namespace}")
        deployments_command = f"kubectl get deployments -n {selected_namespace}"
        deployments_output = run_kubectl_command(deployments_command)
        if deployments_output == "":
            print(f"{colored('No resources found', 'red')} in default namespace.")
            print(deployments_output)
        print(deployments_output)
    else:
        print("No namespace selected.")

def check_deployment_status():
    """Function to check the rollout status of a deployment in a selected namespace."""
    namespaces = run_kubectl_command("kubectl get ns --no-headers -o custom-columns=:metadata.name").splitlines()
    if not namespaces:
        print("No namespaces found.")
        return

    questions = [
        inquirer.List(
            "namespace",
            message="Select a Kubernetes namespace:",
            choices=namespaces,
            carousel=True
        ),
    ]

    answers = inquirer.prompt(questions)
    if answers is None:
        print("No namespace selected.")
        return

    selected_namespace = answers.get('namespace')
    if selected_namespace:
        print(f"Select a deployment in namespace: {selected_namespace}")
        deployments = run_kubectl_command(
            f"kubectl get deployments -n {selected_namespace} --no-headers -o custom-columns=:metadata.name").splitlines()

        if not deployments:
            print(f"No deployments found in namespace {selected_namespace}.")
            return

        deployment_question = [
            inquirer.List(
                "deployment",
                message="Select a deployment:",
                choices=deployments,
                carousel=True
            ),
        ]

        deployment_answers = inquirer.prompt(deployment_question)
        if deployment_answers is None:
            print("No deployment selected.")
            return

        selected_deployment = deployment_answers.get('deployment')
        # Check the rollout status...
        if selected_deployment:
            print(f"Checking rollout status of deployment: {selected_deployment} in namespace: {selected_namespace}")
            rollout_command = f"kubectl rollout status deployment/{selected_deployment} -n {selected_namespace}"
            rollout_output = run_kubectl_command(rollout_command)
            print(rollout_output)
        else:
            print("No deployment selected.")
    else:
        print("No namespace selected.")

def cordon_node():
    """Function to cordon a Kubernetes node."""
    nodes = run_kubectl_command("kubectl get nodes --no-headers -o custom-columns=:metadata.name").splitlines()
    if not nodes:
        print("No nodes found.")
        return

    questions = [
        inquirer.List(
            "node",
            message="Select a node to cordon:",
            choices=nodes,
            carousel=True
        ),
    ]

    answers = inquirer.prompt(questions)
    if answers is None:
        print("No node selected.")
        return

    selected_node = answers.get('node')
    # Cordon the selected node
    if selected_node:
        print(f"Cording node: {selected_node}")
        cordon_command = f"kubectl cordon {selected_node}"
        cordon_output = run_kubectl_command(cordon_command)
        print(cordon_output)
    else:
        print("No node selected.")

def list_pods_on_node():
    """Function to list pods on a selected node in a specific namespace."""
    nodes = run_kubectl_command("kubectl get nodes --no-headers -o custom-columns=:metadata.name").splitlines()
    if not nodes:
        print("No nodes found.")
        return

    questions = [
        inquirer.List(
            "node",
            message="Select a node to list pods:",
            choices=nodes,
            carousel=True
        ),
    ]

    answers = inquirer.prompt(questions)
    if answers is None:
        print("No node selected.")
        return

    selected_node = answers.get('node')
    namespaces = run_kubectl_command("kubectl get ns --no-headers -o custom-columns=:metadata.name").splitlines()
    if not namespaces:
        print("No namespaces found.")
        return

    namespace_question = [
        inquirer.List(
            "namespace",
            message="Select a namespace:",
            choices=namespaces,
            carousel=True
        ),
    ]

    namespace_answers = inquirer.prompt(namespace_question)
    if namespace_answers is None:
        print("No namespace selected.")
        return

    selected_namespace = namespace_answers.get('namespace')
    if selected_node and selected_namespace:
        print(f"Listing pods on node: {selected_node} in namespace: {selected_namespace}")
        pods_command = f"kubectl get pods --field-selector spec.nodeName={selected_node} -n {selected_namespace}"
        pods_output = run_kubectl_command(pods_command)
        print(pods_output)
    else:
        print("No node or namespace selected.")

def list_pods_on_all_nodes():
    """Function to list all pods across all nodes."""
    command = "kubectl get pod -o=custom-columns=NAME:.metadata.name,STATUS:.status.phase,NODE:.spec.nodeName --all-namespaces"
    output = run_kubectl_command(command)
    print("Listing all pods across all nodes:")
    print(output)

def list_pod_images():
    """Function to list pod images in a selected namespace."""
    namespaces = run_kubectl_command("kubectl get ns --no-headers -o custom-columns=:metadata.name").splitlines()
    if not namespaces:
        print("No namespaces found.")
        return

    questions = [
        inquirer.List(
            "namespace",
            message="Select a namespace to list pod images:",
            choices=namespaces,
            carousel=True
        ),
    ]

    answers = inquirer.prompt(questions)
    if answers is None:
        print("No namespace selected.")
        return

    selected_namespace = answers.get('namespace')
    if selected_namespace:
        print(f"Listing all pod images in namespace: {selected_namespace}")
        command = f"kubectl get pods -n {selected_namespace} -o jsonpath='{{range .items[*]}}{{.metadata.name}}{{\"\\t\"}}{{range .spec.containers[*]}}{{.image}}{{\"\\n\"}}{{end}}{{end}}'"
        pods_output = run_kubectl_command(command)

        if pods_output:
            print("Pod Name\t\t\t\t\t\t\tImage")
            # Formatting the output to resemble a table (TODO)
            for line in pods_output.splitlines():
                columns = line.split("\t")
                print(f"{columns[0]:<40} {columns[1]}")
        else:
            print(f"No pods found in namespace: {selected_namespace}")
    else:
        print("No namespace selected.")

def restart_deployment():
    """Function to restart a deployment in a selected namespace."""
    namespaces = run_kubectl_command("kubectl get ns --no-headers -o custom-columns=:metadata.name").splitlines()
    if not namespaces:
        print("No namespaces found.")
        return

    questions = [
        inquirer.List(
            "namespace",
            message="Select a namespace to restart a deployment:",
            choices=namespaces,
            carousel=True
        ),
    ]

    answers = inquirer.prompt(questions)
    if answers is None:
        print("No namespace selected.")
        return

    selected_namespace = answers.get('namespace')
    if selected_namespace:
        print(f"Select a deployment to restart in namespace: {selected_namespace}")
        command = f"kubectl get deployments -n {selected_namespace} --no-headers -o custom-columns=:metadata.name"
        deployments = run_kubectl_command(command).splitlines()

        if not deployments:
            print(f"No deployments found in namespace: {selected_namespace}")
            return

        deployment_question = [
            inquirer.List(
                "deployment",
                message=f"Select a deployment to restart in namespace: {selected_namespace}",
                choices=deployments,
                carousel=True
            ),
        ]

        deployment_answers = inquirer.prompt(deployment_question)
        if deployment_answers is None:
            print("No deployment selected.")
            return

        selected_deployment = deployment_answers.get('deployment')
        if selected_deployment:
            print(f"Restarting deployment: {selected_deployment} in namespace: {selected_namespace}")
            restart_command = f"kubectl rollout restart deployment/{selected_deployment} -n {selected_namespace}"
            run_kubectl_command(restart_command)
            print(f"Deployment {selected_deployment} in namespace {selected_namespace} has been restarted.")
        else:
            print("No deployment selected.")
    else:
        print("No namespace selected.")


def check_crash_log():
    """Function to check logs of a crashed pod."""
    namespaces = run_kubectl_command("kubectl get ns --no-headers -o custom-columns=:metadata.name").splitlines()

    if not namespaces:
        print("No namespaces found.")
        return

    questions = [
        inquirer.List(
            "namespace",
            message="Select a namespace to check logs of a crashed pod:",
            choices=namespaces,
            carousel=True
        ),
    ]

    answers = inquirer.prompt(questions)
    if answers is None:
        print("No namespace selected. Exiting.")
        sys.exit(1)

    selected_namespace = answers.get('namespace')
    if selected_namespace:
        print(f"Select a crashed pod in namespace: {selected_namespace}")
        command = f"kubectl get pods -n {selected_namespace} --field-selector=status.phase!=Running --no-headers -o custom-columns=:metadata.name"
        crashed_pods = run_kubectl_command(command).splitlines()
        if not crashed_pods:
            print(f"No crashed pods found in namespace: {selected_namespace}")
            return

        pod_question = [
            inquirer.List(
                "pod",
                message=f"Select a crashed pod in namespace: {selected_namespace}",
                choices=crashed_pods,
                carousel=True
            ),
        ]

        pod_answers = inquirer.prompt(pod_question)
        if pod_answers is None:
            print("No pod selected. Exiting.")
            sys.exit(1)

        selected_pod = pod_answers.get('pod')
        if selected_pod:
            print(f"Fetching logs for pod: {selected_pod} in namespace: {selected_namespace}")
            log_command = f"kubectl logs {selected_pod} -n {selected_namespace} -p"
            pod_logs = run_kubectl_command(log_command)
            print(pod_logs)
        else:
            print("No pod selected.")
    else:
        print("No namespace selected. Exiting.")
        sys.exit(1)

def get_events():
    """Function to fetch events for a selected namespace."""
    namespaces = run_kubectl_command("kubectl get ns --no-headers -o custom-columns=:metadata.name").splitlines()

    if not namespaces:
        print("No namespaces found.")
        return

    questions = [
        inquirer.List(
            "namespace",
            message="Select a namespace to get events:",
            choices=namespaces,
            carousel=True
        ),
    ]

    answers = inquirer.prompt(questions)
    if answers is None:
        print("No namespace selected. Exiting.")
        sys.exit(1)

    selected_namespace = answers.get('namespace')
    if selected_namespace:
        print(f"Fetching events for namespace: {selected_namespace}")
        command = f"kubectl get events -n {selected_namespace} --sort-by='.lastTimestamp' -o wide"
        events_output = run_kubectl_command(command)

        if events_output:
            print(events_output)
        else:
            print(f"No events found in namespace: {selected_namespace}")
    else:
        print("No namespace selected. Exiting.")
        sys.exit(1)

def get_all_events():
    """Function to fetch all events across all namespaces."""
    print("Fetching all events across all namespaces...")
    command = "kubectl get events -A --sort-by='.lastTimestamp' -o wide"
    events_output = run_kubectl_command(command)
    if events_output:
        print(events_output)
    else:
        print("No events found.")

def list_pods_with_labels():
    """Function to list pods with labels in a selected namespace."""
    namespaces = run_kubectl_command("kubectl get ns --no-headers -o custom-columns=:metadata.name").splitlines()
    if not namespaces:
        print("No namespaces found.")
        return

    questions = [
        inquirer.List(
            "namespace",
            message="Select a namespace to list pods with labels:",
            choices=namespaces,
            carousel=True
        ),
    ]

    answers = inquirer.prompt(questions)
    if answers is None:
        print("No namespace selected. Exiting.")
        sys.exit(1)

    selected_namespace = answers.get('namespace')
    if selected_namespace:
        print(f"Listing pods with labels in namespace: {selected_namespace}")
        command = f"kubectl get pods --show-labels -n {selected_namespace}"
        pods_with_labels = run_kubectl_command(command)
        if pods_with_labels:
            print(pods_with_labels)
        else:
            print(f"No pods found in namespace: {selected_namespace}")
    else:
        print("No namespace selected. Exiting.")
        sys.exit(1)

def list_containers():
    """Function to list all containers (init and non-init) in pods within a selected namespace."""
    namespaces = run_kubectl_command("kubectl get ns --no-headers -o custom-columns=:metadata.name").splitlines()
    if not namespaces:
        print("No namespaces found.")
        return

    questions = [
        inquirer.List(
            "namespace",
            message="Select a namespace to list all containers in pods:",
            choices=namespaces,
            carousel=True
        ),
    ]

    answers = inquirer.prompt(questions)
    if answers is None:
        print("No namespace selected. Exiting.")
        sys.exit(1)

    selected_namespace = answers.get('namespace')
    if selected_namespace:
        print(f"Listing all containers (init and non-init) in pods within namespace: {selected_namespace}")
        command = f"kubectl get pod -o='custom-columns=NAME:.metadata.name,INIT-CONTAINERS:.spec.initContainers[].name,CONTAINERS:.spec.containers[].name' -n {selected_namespace}"
        containers_output = run_kubectl_command(command)
        if containers_output:
            print(containers_output)
        else:
            print(f"No containers found in namespace: {selected_namespace}")
    else:
        print("No namespace selected. Exiting.")
        sys.exit(1)

def container_logs():
    """Function to fetch logs for a specific container in a pod within a selected namespace."""
    namespaces = run_kubectl_command("kubectl get ns --no-headers -o custom-columns=:metadata.name").splitlines()
    if not namespaces:
        print("No namespaces found.")
        return

    questions = [
        inquirer.List(
            "namespace",
            message="Select a namespace to get logs for a specific container in a pod:",
            choices=namespaces,
            carousel=True
        ),
    ]

    answers = inquirer.prompt(questions)
    if answers is None:
        print("No namespace selected. Exiting.")
        sys.exit(1)

    selected_namespace = answers.get('namespace')
    print(f"Select a pod in namespace {selected_namespace}:")
    pods = run_kubectl_command(
        f"kubectl get pods -n {selected_namespace} --no-headers -o custom-columns=:metadata.name").splitlines()
    if not pods:
        print(f"No pods found in namespace {selected_namespace}.")
        return

    pod_question = [
        inquirer.List(
            "pod",
            message=f"Select a pod in namespace {selected_namespace}:",
            choices=pods,
            carousel=True
        ),
    ]

    pod_answers = inquirer.prompt(pod_question)
    if pod_answers is None:
        print("No pod selected. Exiting.")
        sys.exit(1)

    selected_pod = pod_answers.get('pod')
    print(f"Select a container in pod {selected_pod}:")
    containers = run_kubectl_command(
        f"kubectl get pod {selected_pod} -n {selected_namespace} -o jsonpath="+'{.spec.containers[*].name}').split()
    if not containers:
        print(f"No containers found in pod {selected_pod}.")
        return

    container_question = [
        inquirer.List(
            "container",
            message=f"Select a container in pod {selected_pod}:",
            choices=containers,
            carousel=True
        ),
    ]

    container_answers = inquirer.prompt(container_question)
    if container_answers is None:
        print("No container selected. Exiting.")
        sys.exit(1)

    selected_container = container_answers.get('container')
    print(
        f"Fetching logs for container {selected_container} in pod {selected_pod} in namespace {selected_namespace}...")
    logs = run_kubectl_command(f"kubectl logs {selected_pod} -n {selected_namespace} -c {selected_container}")
    if logs:
        print(logs)
    else:
        print(f"No logs found for container {selected_container} in pod {selected_pod}.")

def deploy_logs():
    """Function to fetch logs for a specific deployment within a selected namespace."""
    namespaces = run_kubectl_command("kubectl get ns --no-headers -o custom-columns=:metadata.name").splitlines()
    if not namespaces:
        print("No namespaces found.")
        return

    questions = [
        inquirer.List(
            "namespace",
            message="Select a namespace to get logs for a deployment:",
            choices=namespaces,
            carousel=True
        ),
    ]

    answers = inquirer.prompt(questions)
    if answers is None:
        print("No namespace selected. Exiting.")
        sys.exit(1)

    selected_namespace = answers.get('namespace')
    print(f"Select a deployment in namespace {selected_namespace}:")
    deployments = run_kubectl_command(
        f"kubectl get deployments -n {selected_namespace} --no-headers -o custom-columns=:metadata.name").splitlines()
    if not deployments:
        print(f"No deployments found in namespace {selected_namespace}.")
        return

    deployment_question = [
        inquirer.List(
            "deployment",
            message=f"Select a deployment in namespace {selected_namespace}:",
            choices=deployments,
            carousel=True
        ),
    ]

    deployment_answers = inquirer.prompt(deployment_question)
    if deployment_answers is None:
        print("No deployment selected. Exiting.")
        sys.exit(1)

    selected_deployment = deployment_answers.get('deployment')
    print(f"Fetching logs for deployment {selected_deployment} in namespace {selected_namespace}...")
    logs = run_kubectl_command(f"kubectl logs deployment/{selected_deployment} -n {selected_namespace}")

    if logs:
        print(logs)
    else:
        print(f"No logs found for deployment {selected_deployment} in namespace {selected_namespace}.")

def services_logs():
    """Function to fetch logs for a specific service within a selected namespace."""
    namespaces = run_kubectl_command("kubectl get ns --no-headers -o custom-columns=:metadata.name").splitlines()
    if not namespaces:
        print("No namespaces found.")
        return

    questions = [
        inquirer.List(
            "namespace",
            message="Select a namespace to get logs for a service:",
            choices=namespaces,
            carousel=True
        ),
    ]

    answers = inquirer.prompt(questions)
    if answers is None:
        print("No namespace selected. Exiting.")
        sys.exit(1)

    selected_namespace = answers.get('namespace')
    print(f"Select a service in namespace {selected_namespace}:")
    services = run_kubectl_command(
        f"kubectl get services -n {selected_namespace} --no-headers -o custom-columns=:metadata.name").splitlines()
    if not services:
        print(f"No services found in namespace {selected_namespace}.")
        return

    service_question = [
        inquirer.List(
            "service",
            message=f"Select a service in namespace {selected_namespace}:",
            choices=services,
            carousel=True
        ),
    ]

    service_answers = inquirer.prompt(service_question)
    if service_answers is None:
        print("No service selected. Exiting.")
        sys.exit(1)

    selected_service = service_answers.get('service')
    print(f"Fetching logs for service {selected_service} in namespace {selected_namespace}...")
    logs = run_kubectl_command(f"kubectl logs service/{selected_service} -n {selected_namespace}")
    if logs:
        print(logs)
    else:
        print(f"No logs found for service {selected_service} in namespace {selected_namespace}.")

def main():
    while True:
        # Clear screen and show command list
        clear_screen()
        # Print the Welcome KUBERMON message
        ascii_art = pyfiglet.figlet_format("KUBERMON")
        print(ascii_art)
        print("Welcome to Kubemon! (v1.0.0)")
        commands = show_commands()

        # Use inquirer module to select a command with arrow keys
        command_list = [
            inquirer.List(
                "command",
                message="Please select a command:",
                choices=commands,
                carousel=True
            ),
        ]
        get_command_list = inquirer.prompt(command_list)
        if get_command_list is None:
            print("No selection made. Exiting.")
            break

        # Access the selected command
        command = get_command_list.get('command')
        if command == "get-nodes":
            print(run_kubectl_command("kubectl get nodes"))
        elif command == "get-contexts":
            get_contexts()
        elif command == "select-context":
            select_context()
        elif command == "list-namespaces":
            print(run_kubectl_command("kubectl get namespaces"))
        elif command == "not-running-pods":
            list_not_running_pods()
        elif command == "delete-pods":
            delete_pods()
        elif command == "list-deployments":
            list_deployments()
        elif command == "check-deployment-status":
            check_deployment_status()
        elif command == "cordon-nodes":
            cordon_node()
        elif command == "list-pods":
            list_pods_on_node()
        elif command == "list-pods-on-nodes":
            list_pods_on_all_nodes()
        elif command == "image-version":
            list_pod_images()
        elif command == "restart-deployment":
            restart_deployment()
        elif command == "check-crash-log":
            check_crash_log()
        elif command == "events":
            get_events()
        elif command == "all-events":
            get_all_events()
        elif command == "list-pod-with-labels":
            list_pods_with_labels()
        elif command == "list-containers":
            list_containers()
        elif command == "container-logs":
            container_logs()
        elif command == "deploy-logs":
            deploy_logs()
        elif command == "services-logs":
            services_logs()
        else:
            print(f"Unknown command: {command}")
        # wants to continue or exit
        continue_prompt = input("\nDo you want to run another command? (y/n): ").strip().lower()
        if continue_prompt != 'y':
            print("Exiting Kubemon.")
            break


if __name__ == "__main__":
    main()