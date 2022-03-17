import cowsay
from src import run_backend, run_frontend
from src.cloud_manager import setup_cluster
from src.dialog import get_user_input
from src.system_information import get_system_state

docker_frontend_tag = '0.0.1'
contexts, active_context, is_debug = get_system_state()
user_input = get_user_input(contexts, active_context)
setup_cluster(user_input.cluster, user_input.new_cluster_type)
(
    gateway_host,
    gateway_port,
    gateway_host_internal,
    gateway_port_internal,
) = run_backend.run(user_input, is_debug)
frontend_host, frontend_port = run_frontend.run(
    user_input.dataset,
    gateway_host,
    gateway_port,
    gateway_host_internal,
    gateway_port_internal,
    docker_frontend_tag,
)
url = f'{frontend_host}' + ('' if str(frontend_port) == '80' else f':{frontend_port}')
print()

# print(f'✅ Your search case running.\nhost: {node_ip}:30080')
# print(f'host: {node_ip}:30080')
cowsay.cow(f'You made it:\n{url}')
