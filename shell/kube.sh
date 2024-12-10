#!/bin/bash


CURRENT_CONTEXT=$(kubectl config current-context)


figlet KUBERMON
echo "Welcome to Kubemon! (v1.0.0)"


show_commands() {
    echo -e "get-nodes"
    echo -e "get-contexts"
    echo -e "select-context"
    echo -e "list-namespaces"
    echo -e "not-running-pods"
    echo -e "delete-pods"
    echo -e "list-deployments"
    echo -e "check-deployment-status"
    echo -e "cordon-nodes"
    echo -e "list-pods"
    echo -e "list-pods-on-nodes"
    echo -e "image-version"
    echo -e "restart-deployment"
    echo -e "events"
    echo -e "all-events"
    echo -e "list-pod-with-labels"
    echo -e "list-containers"
    echo -e "container-logs"
    echo -e "check-crash-log"
    echo -e "deploy-logs"
    echo -e "services-logs"
    echo -e "Please select a command:"
}

if [ -z "$1" ]; then
    COMMAND=$(show_commands | fzf --height 60% --border --ansi --header="Select a command")
    if [ -z "$COMMAND" ]; then
        echo "No command selected. Exiting."
        exit 1
    fi
    set -- "$COMMAND"
fi

case "$1" in
    get-nodes)
        echo "Fetching the list of nodes in the Kubernetes cluster..."
        kubectl get nodes
        ;;
    get-contexts)
        echo "Fetching the list of Kubernetes contexts..."
        kubectl config get-contexts | awk -v curr="$CURRENT_CONTEXT" '{if ($1 == "*" || $2 == curr) {printf "\033[1;32m%s\033[0m\n", $0} else {print}}'
        ;;
    select-context)
        echo "Select a context from the list:"
        SELECTED_CONTEXT=$(kubectl config get-contexts -o name | fzf --height 40% --border --ansi --header="Select a Kubernetes context")
        if [ -n "$SELECTED_CONTEXT" ]; then
            echo "Switching to context: $SELECTED_CONTEXT"
            kubectl config use-context "$SELECTED_CONTEXT"
            echo "Switched to context: $SELECTED_CONTEXT"
        else
            echo "No context selected."
        fi
        ;;
    list-namespaces)
        echo "Listing all namespaces.."
        kubectl get ns
        ;;
    not-running-pods)
        echo "List all pods not in the Running state in a specific namespace:"
        NAMESPACE=$(kubectl get ns --no-headers | awk '{print $1}' | fzf --height 40% --border --ansi --header="Select a Kubernetes namespace")
        if [ -n "$NAMESPACE" ]; then
            kubectl get pods -n "$NAMESPACE" --field-selector=status.phase!=Running
        else
            echo "No namespace selected."
        fi
        ;;
    delete-pods)
        echo "Select a namespace to delete pods not in Running state:"
        NAMESPACE=$(kubectl get ns --no-headers | awk '{print $1}' | fzf --height 40% --border --ansi --header="Select a Kubernetes namespace")
        if [ -n "$NAMESPACE" ]; then
            echo "Deleting pods not in Running state in namespace: $NAMESPACE"
            kubectl delete pods --namespace "$NAMESPACE" --field-selector=status.phase!=Running --grace-period=0 --force
            echo "Deletion complete."
        else
            echo "No namespace selected."
        fi
        ;;
    list-deployments)
        echo "Select a namespace to list deployments:"
        NAMESPACE=$(kubectl get ns --no-headers | awk '{print $1}' | fzf --height 40% --border --ansi --header="Select a Kubernetes namespace")
        if [ -n "$NAMESPACE" ]; then
            echo "Listing deployments in namespace: $NAMESPACE"
            kubectl get deployments -n "$NAMESPACE"
        else
            echo "No namespace selected."
        fi
        ;;
    check-deployment-status)
        echo "Select a namespace:"
        NAMESPACE=$(kubectl get ns --no-headers | awk '{print $1}' | fzf --height 40% --border --ansi --header="Select a Kubernetes namespace")
        if [ -n "$NAMESPACE" ]; then
            echo "Select a deployment in namespace $NAMESPACE:"
            DEPLOYMENT=$(kubectl get deployments -n "$NAMESPACE" --no-headers | awk '{print $1}' | fzf --height 40% --border --ansi --header="Select a deployment")
            if [ -n "$DEPLOYMENT" ]; then
                echo "Checking rollout status of deployment: $DEPLOYMENT in namespace: $NAMESPACE"
                kubectl rollout status deployment/"$DEPLOYMENT" -n "$NAMESPACE"
            else
                echo "No deployment selected."
            fi
        else
            echo "No namespace selected."
        fi
        ;;
    cordon-nodes)
        echo "Select a cordon node:"
        NODE=$(kubectl get nodes --no-headers | awk '{print $1}' | fzf --height 40% --border --ansi --header="Select a node")
        if [ -n "$NODE" ]; then
            kubectl cordon "$NODE"
            echo "Node $NODE cordoned."
        else
            echo "No node selected."
        fi
        ;;
    list-pods)
        echo "Select a node to list pods:"
        NODE=$(kubectl get nodes --no-headers | awk '{print $1}' | fzf --height 40% --border --ansi --header="Select a node")
        if [ -n "$NODE" ]; then
            echo "Select a namespace:"
            NAMESPACE=$(kubectl get ns --no-headers | awk '{print $1}' | fzf --height 40% --border --ansi --header="Select a namespace")
            if [ -n "$NAMESPACE" ]; then
                echo "Listing pods on node: $NODE in namespace: $NAMESPACE"
                kubectl get pods --field-selector spec.nodeName="$NODE" -n "$NAMESPACE"
            else
                echo "No namespace selected."
            fi
        else
            echo "No node selected."
        fi
        ;;
    list-pods-on-nodes)
        echo "Listing all pods across all nodes:"
        kubectl get pod -o=custom-columns=NAME:.metadata.name,STATUS:.status.phase,NODE:.spec.nodeName --all-namespaces
        ;;
    image-version)
        echo "Select a namespace to list pod images:"
        NAMESPACE=$(kubectl get ns --no-headers | awk '{print $1}' | fzf --height 40% --border --ansi --header="Select a namespace")
        if [ -n "$NAMESPACE" ]; then
            echo "Listing all pod images in namespace: $NAMESPACE"
            PODS=$(kubectl get pods -n "$NAMESPACE" -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{range .spec.containers[*]}{.image}{"\n"}{end}{end}')
            
            if [ -n "$PODS" ]; then
                echo -e "Pod Name\t\t\t\t\t\t\tImage"
                echo "$PODS" | column -t
            else
                echo "No pods found in namespace: $NAMESPACE"
            fi
        else
            echo "No namespace selected."
        fi
        ;;
    restart-deployment)
        echo "Select a namespace to restart a deployment:"
        NAMESPACE=$(kubectl get ns --no-headers | awk '{print $1}' | fzf --height 40% --border --ansi --header="Select a namespace")
        if [ -n "$NAMESPACE" ]; then
            echo "Select a deployment to restart in namespace $NAMESPACE:"
            DEPLOYMENT=$(kubectl get deployments -n "$NAMESPACE" --no-headers | awk '{print $1}' | fzf --height 40% --border --ansi --header="Select a deployment")
            if [ -n "$DEPLOYMENT" ]; then
                echo "Restarting deployment: $DEPLOYMENT in namespace: $NAMESPACE"
                kubectl rollout restart deployment/"$DEPLOYMENT" -n "$NAMESPACE"
                echo "Deployment $DEPLOYMENT in namespace $NAMESPACE has been restarted."
            else
                echo "No deployment selected."
            fi
        else
            echo "No namespace selected."
        fi
        ;;
      check-crash-log)
        echo "Select a namespace to check logs of a crashed pod:"
        NAMESPACE=$(kubectl get ns --no-headers | awk '{print $1}' | fzf --height 40% --border --ansi --header="Select a Kubernetes namespace")

        if [ -z "$NAMESPACE" ]; then
            echo "No namespace selected. Exiting."
            exit 1
        fi

        echo "Select a crashed pod:"
        POD=$(kubectl get pods -n "$NAMESPACE" --field-selector=status.phase!=Running --no-headers | awk '{print $1}' | fzf --height 40% --border --ansi --header="Select a crashed pod")

        if [ -z "$POD" ]; then
            echo "No pod selected. Exiting."
            exit 1
        fi

        echo "Fetching logs for pod: $POD in namespace: $NAMESPACE"
        kubectl logs "$POD" -n "$NAMESPACE" -p
        ;;
     events)
        echo "Select a namespace to get events:"
        NAMESPACE=$(kubectl get ns --no-headers | awk '{print $1}' | fzf --height 40% --border --ansi --header="Select a Kubernetes namespace")

        if [ -z "$NAMESPACE" ]; then
            echo "No namespace selected. Exiting."
            exit 1
        fi

        echo "Fetching events for namespace: $NAMESPACE"
        kubectl get events -n "$NAMESPACE" --sort-by='.lastTimestamp' -o wide
        ;;
    all-events)
        echo "Fetching all events across all namespaces..."
        kubectl get events -A --sort-by='.lastTimestamp' -o wide
        ;;
    list-pod-with-labels)
        echo "Select a namespace to list pods with labels:"
        NAMESPACE=$(kubectl get ns --no-headers | awk '{print $1}' | fzf --height 40% --border --ansi --header="Select a Kubernetes namespace")

        if [ -z "$NAMESPACE" ]; then
            echo "No namespace selected. Exiting."
            exit 1
        fi

        echo "Listing pods with labels in namespace: $NAMESPACE"
        kubectl get pods --show-labels -n "$NAMESPACE"
        ;;
    list-containers)
        echo "Select a namespace to list all containers in pods:"
        NAMESPACE=$(kubectl get ns --no-headers | awk '{print $1}' | fzf --height 40% --border --ansi --header="Select a Kubernetes namespace")

        if [ -z "$NAMESPACE" ]; then
            echo "No namespace selected. Exiting."
            exit 1
        fi

        echo "Listing all containers (init and non-init) in pods within namespace: $NAMESPACE"
        kubectl get pod -o="custom-columns=NAME:.metadata.name,INIT-CONTAINERS:.spec.initContainers[].name,CONTAINERS:.spec.containers[].name" -n "$NAMESPACE"
        ;;
    container-logs)
        echo "Select a namespace to get logs for a specific container in a pod:"
        NAMESPACE=$(kubectl get ns --no-headers | awk '{print $1}' | fzf --height 40% --border --ansi --header="Select a Kubernetes namespace")

        if [ -z "$NAMESPACE" ]; then
            echo "No namespace selected. Exiting."
            exit 1
        fi

        echo "Select a pod in namespace $NAMESPACE:"
        POD=$(kubectl get pods -n "$NAMESPACE" --no-headers | awk '{print $1}' | fzf --height 40% --border --ansi --header="Select a pod")

        if [ -z "$POD" ]; then
            echo "No pod selected. Exiting."
            exit 1
        fi

        echo "Select a container in pod $POD:"
        CONTAINER=$(kubectl get pod "$POD" -n "$NAMESPACE" -o jsonpath='{.spec.containers[*].name}' | tr ' ' '\n' | fzf --height 40% --border --ansi --header="Select a container")

        if [ -z "$CONTAINER" ]; then
            echo "No container selected. Exiting."
            exit 1
        fi

        echo "Fetching logs for container $CONTAINER in pod $POD in namespace $NAMESPACE..."
        kubectl logs "$POD" -n "$NAMESPACE" -c "$CONTAINER"
        ;;
    deploy-logs)
        echo "Select a namespace to get logs for a deployment:"
        NAMESPACE=$(kubectl get ns --no-headers | awk '{print $1}' | fzf --height 40% --border --ansi --header="Select a Kubernetes namespace")

        if [ -z "$NAMESPACE" ]; then
            echo "No namespace selected. Exiting."
            exit 1
        fi

        echo "Select a deployment in namespace $NAMESPACE:"
        DEPLOYMENT=$(kubectl get deployments -n "$NAMESPACE" --no-headers | awk '{print $1}' | fzf --height 40% --border --ansi --header="Select a deployment")

        if [ -z "$DEPLOYMENT" ]; then
            echo "No deployment selected. Exiting."
            exit 1
        fi

        echo "Fetching logs for deployment $DEPLOYMENT in namespace $NAMESPACE..."
        kubectl logs deployment/"$DEPLOYMENT" -n "$NAMESPACE"
        ;;
    services-logs)
        echo "Select a namespace to get logs for a service:"
        NAMESPACE=$(kubectl get ns --no-headers | awk '{print $1}' | fzf --height 40% --border --ansi --header="Select a Kubernetes namespace")

        if [ -z "$NAMESPACE" ]; then
            echo "No namespace selected. Exiting."
            exit 1
        fi

        echo "Select a service in namespace $NAMESPACE:"
        SERVICE=$(kubectl get services -n "$NAMESPACE" --no-headers | awk '{print $1}' | fzf --height 40% --border --ansi --header="Select a service")

        if [ -z "$SERVICE" ]; then
            echo "No service selected. Exiting."
            exit 1
        fi

        echo "Fetching logs for service $SERVICE in namespace $NAMESPACE..."
        kubectl logs service/"$SERVICE" -n "$NAMESPACE"
        ;;
    *)
        echo -e "Available commands:\n"
        show_commands
        exit 1
        ;;
esac
