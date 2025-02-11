import pytest
import os
from testcontainers.core.container import DockerContainer
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
    
    yield container
    
    container.stop()
    container.remove()

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

