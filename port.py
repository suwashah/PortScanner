import time
import socket
from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap

app = Flask(__name__)
bootstrap = Bootstrap(app)


class PortScanResult:
    def __init__(self, port, status, service=None):
        self.port = port
        self.status = status
        self.service = service


def scan_ports(target, start_port, end_port, port_type):
    open_count = 0
    closed_count = 0
    filtered_count = 0
    results = []
    service = ""
    start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    for port in range(start_port, end_port + 1):
        service = "-"
        # start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)  # Timeout for connection attempt
        result = sock.connect_ex((target, port))
        sock.close()
        # finish_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        if port_type == 1 and result == 0:
            open_count += 1
            try:
                service = socket.getservbyport(port)
            except OSError:
                service = "unknown"

            results.append(PortScanResult(port, "open", service))
        # Connection refused (port closed)
        elif port_type == 2 and result == 11:
            closed_count += 1
            results.append(PortScanResult(port, "closed", service))
        elif port_type == 3 and result != 0 and result != 11:
            filtered_count += 1
            # results.append(PortScanResult(port, "filtered", service))
        elif port_type == 0:
            if result == 0:
                open_count += 1
                try:
                    service = socket.getservbyport(port)
                except OSError:
                    service = "unknown"

                results.append(PortScanResult(port, "open", service))
            elif result == 11:
                closed_count += 1
                results.append(PortScanResult(port, "closed", service))
            else:
                filtered_count += 1
                # results.append(PortScanResult(port, "filtered", service))

    finish_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    return results, open_count, closed_count, filtered_count, start_time, finish_time


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        target = request.form['target']
        start_port = int(request.form['start_port'])
        end_port = int(request.form['end_port'])
        port_type = int(request.form['port_type'])

        scan_results, open_count, closed_count, filtered_count, start_time, finish_time = scan_ports(
            target, start_port, end_port, port_type)

        return render_template('index.html', target=target, start_port=start_port, end_port=end_port,
                               scan_results=scan_results, open_count=open_count, closed_count=closed_count, filtered_count=filtered_count, start_time=start_time, finish_time=finish_time)
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
