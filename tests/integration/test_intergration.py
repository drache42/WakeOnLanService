import pytest
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs
from time import sleep

@pytest.fixture(scope="session")
def docker_container():
    # Build the Docker image from the Dockerfile
    import docker
    client = docker.from_env()
    client.images.build(path=".", dockerfile="docker/Dockerfile", tag="wakeonlanservice:test")

    # Run the container
    container = DockerContainer("wakeonlanservice:test")
    container.with_bind_ports(4200, 4200)

    # Set the environment variables
    container.with_env("MAC_ADDRESS", "18:C0:4D:07:5B:2D")
    container.with_env("URL", "https://example.com")

    container.start()

    try:
        duration = wait_for_logs(container, "wakeonlanservice: App created successfully", timeout=360)
        print(f"Container started successfully after {duration} seconds")
    except Exception as e:
        print(f"Failed to find log message: {e}")
        container.stop()
        pytest.fail("Failed to find log message within the timeout period")
    
    yield container
    
    container.stop()

def test_container_health_check(docker_container):
    # Wait for the container to start and become healthy
    wrapped_container = docker_container.get_wrapped_container()
    for _ in range(3):
        wrapped_container.reload()
        health_status = wrapped_container.attrs.get("State", {}).get("Health", {}).get("Status", {})
        if health_status == "healthy":
            break
        sleep(10)
    else:
        # Log container output for debugging
        logs = wrapped_container.logs().decode("utf-8")
        print(f"Container logs: {logs}")
        pytest.fail("Container did not become healthy in time")

