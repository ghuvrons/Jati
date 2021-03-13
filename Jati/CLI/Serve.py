import sys, os, Jati

class Serve:
    def run(self, host = "127.0.0.1", port=3000, isSSL = False, log_file = None):
        current_dir = os.getcwd()
        if current_dir not in sys.path:
            sys.path.insert(1, current_dir)
        try:
            jati = Jati.Jati(host=host, port=port, isSSL=isSSL, log_file=log_file)
            jati.addVHost({'localhost': 'localhost'})
            jati.start()
        except KeyboardInterrupt:
            print("closing")
            jati.close()