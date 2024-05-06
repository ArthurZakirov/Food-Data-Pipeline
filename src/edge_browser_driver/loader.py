from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service


def load_driver(edge_options_dict):

    print(edge_options_dict)

    edge_options = Options()
    edge_options.use_chromium = True
    edge_options.add_experimental_option(
        "debuggerAddress", f"localhost:{edge_options_dict['remote_debugging_port']}"
    )

    service = Service(edge_options_dict["edge_driver_path"])
    driver = webdriver.Edge(service=service, options=edge_options)
    driver.get(f"{edge_options_dict['url']}")
    return driver
