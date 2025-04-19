import pytest
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs
from time import sleep
import logging

logger = logging.getLogger(__name__)

@pytest.fixture(scope="session")
def docker_container():
    logger.info("Starting container fixture setup")
    
    # Build the Docker image from the Dockerfile
    import docker
    client = docker.from_env()
    logger.info("Building Docker image from Dockerfile")
    try:
        client.images.build(path=".", dockerfile="docker/Dockerfile", tag="wakeonlanservice:test")
        logger.debug("Docker image build successful")
    except Exception as e:
        logger.error(f"Docker image build failed: {e}")
        pytest.fail(f"Failed to build Docker image: {e}")

    # Run the container
    logger.info("Setting up Docker container")
    container = DockerContainer("wakeonlanservice:test")
    container.with_bind_ports(4200, 4200)
    logger.debug("Configured port binding 4200:4200")

    # Set the environment variables
    container.with_env("MAC_ADDRESS", "18:C0:4D:07:5B:2D")
    container.with_env("URL", "https://example.com")
    logger.debug("Environment variables configured")

    logger.info("Starting container")
    container.start()
    logger.debug(f"Container started with ID: {container.get_wrapped_container().id}")

    try:
        logger.info("Waiting for application startup log message...")
        duration = wait_for_logs(container, "wakeonlanservice: App created successfully", timeout=360)
        logger.info(f"Container started successfully after {duration} seconds")
    except Exception as e:
        logger.error(f"Failed to find log message: {e}")
        logger.debug("Retrieving container logs for troubleshooting")
        try:
            logs = container.get_logs()
            logger.debug(f"Container logs: {logs}")
        except Exception as log_e:
            logger.error(f"Failed to retrieve logs: {log_e}")
        container.stop()
        pytest.fail("Failed to find log message within the timeout period")
    
    logger.info("Container fixture setup complete, yielding container")
    yield container
    
    logger.info("Stopping and cleaning up container")
    container.stop()
    logger.info("Container stopped successfully")

def test_container_health_check(docker_container):
    logger.info("Starting container health check test")
    # Wait for the container to start and become healthy
    wrapped_container = docker_container.get_wrapped_container()
    logger.debug(f"Obtained wrapped container with ID: {wrapped_container.id}")
    
    healthy = False
    for attempt in range(1, 11):
        logger.info(f"Health check attempt {attempt}/10")
        wrapped_container.reload()
        health_status = wrapped_container.attrs.get("State", {}).get("Health", {}).get("Status", {})
        logger.debug(f"Current health status: {health_status}")
        
        if health_status == "healthy":
            logger.info("Container is healthy")
            healthy = True
            break
        else:
            state_details = wrapped_container.attrs.get("State", {})
            logger.info(f"Container not yet healthy, state: {state_details}")
            
            # Get health check details if available
            health_checks = wrapped_container.attrs.get("State", {}).get("Health", {}).get("Log", [])
            if health_checks:
                last_check = health_checks[-1]
                logger.debug(f"Last health check: {last_check}")
                
        logger.info("Waiting 10 seconds before next health check")
        sleep(10)
    
    if not healthy:
        # Log container output for debugging
        logger.error("Container failed to become healthy in time")
        logs = wrapped_container.logs().decode("utf-8")
        logger.info(f"Container logs: {logs}")
        
        # Get more detailed diagnostics
        logger.debug("Container inspection details:")
        logger.debug(f"Container status: {wrapped_container.status}")
        logger.debug(f"Container state: {wrapped_container.attrs.get('State')}")
        
        pytest.fail("Container did not become healthy in time")
    
    logger.info("Health check test completed successfully")

