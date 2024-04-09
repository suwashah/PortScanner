from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
import socket
app = Flask(__name__)
bootstrap = Bootstrap(app)


class PortScanResult:
    def __init__(self, port, status, service=None, protocol=None, service_product=None):
        self.port = port
        self.status = status
        self.service = service
        self.protocol = protocol
        self.service_product = service_product


def scan_ports(target, start_port, end_port, port_type):
    protocol = None
    service_product = None
    results = []
    service = ""
    for port in range(start_port, end_port + 1):
        service = ""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)  # Timeout for connection attempt
        result = sock.connect_ex((target, port))
        sock.close()
        if port_type == 1 and result == 0:
            try:
                service = socket.getservbyport(port)
            except OSError:
                service = "Unknown"

            results.append(PortScanResult(
                port, "open", service, protocol, service_product))
        # Connection refused (port closed)
        elif port_type == 2 and result == 11:
            results.append(PortScanResult(port, "closed"))
        elif port_type == 3 and result != 0 and result != 11:
            results.append(PortScanResult(port, "filtered"))
        elif port_type == 0:
            if result == 0:
                try:
                    service = socket.getservbyport(port)
                except OSError:
                    service = "Unknown"

                results.append(PortScanResult(
                    port, "open", service, protocol, service_product))
            elif result == 11:
                results.append(PortScanResult(port, "closed"))
            else:
                results.append(PortScanResult(port, "filtered"))

    return results


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        target = request.form['target']
        start_port = int(request.form['start_port'])
        end_port = int(request.form['end_port'])
        port_type = int(request.form['port_type'])

        scan_results = scan_ports(
            target, start_port, end_port, port_type)

        return render_template('index.html', target=target, start_port=start_port, end_port=end_port,
                               scan_results=scan_results)
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
