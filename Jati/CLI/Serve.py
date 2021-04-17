import sys, os, Jati

class Serve:
    def run(self, host, port, sites, log_file, isSSL):
        current_dir = os.getcwd()
        if current_dir not in sys.path:
            sys.path.insert(1, current_dir)
        try:
            jati = Jati.Jati(host=host, port=port, isSSL=None, log_file=log_file)
            jati.addVHost(sites)
            jati.start()
        except KeyboardInterrupt:
            print("closing")
            jati.close()