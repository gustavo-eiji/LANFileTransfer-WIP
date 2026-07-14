from devicemanager import DeviceManager
from discovery import Discovery
import uuid

from gui import MainWindow
from transfer import TransferServer, TransferClient


# TODO:
# Discovery and TransferServer will eventually run in background threads.
# The GUI will become the application's main loop and call stop() on exit.

def main():
    # Generates unique ID
    device_id = str(uuid.uuid4())

    device_manager = DeviceManager()

    discovery = Discovery(device_manager, device_id)

    transfer_server = TransferServer()

    transfer_client = TransferClient()

    gui = MainWindow(
        device_manager=device_manager,
        discovery=discovery,
        transfer_server=transfer_server,
        transfer_client=transfer_client,
    )


    gui.run()

    try:
        # Advertises this computer to the network
        # Initiates listening for other computers (Zeroconf)
        discovery.start()
        transfer_server.start()

        #input("\nPress Enter to exit...\n")

    finally:
        transfer_server.stop()
        discovery.stop()

if __name__ == "__main__":
    main()
