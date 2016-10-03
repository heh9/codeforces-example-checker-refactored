import os, sys, urllib.request, re, subprocess, bs4, json

EXTENSIONS_MAP = 'extensions-map.json'
CONFIG_FILE = 'settings.json'

"Loading configs"
with open(CONFIG_FILE) as cfg_file:
    cfg = json.load(cfg_file)
    SAVE_PATH = cfg['save_path']

class ExampleParser:
    def __init__(self, link):
        """Downloads the page and makes it a bs4 tree"""
        pat = r"(\d+)\/(\w+)"
        matches = re.findall(pat, link)[0]
        self.contest_name = matches[0]
        self.problem_name = matches[1]
        self.link = link

    def get_examples(self):
        """Returns an array of tests"""
        contest_path = SAVE_PATH + '/' + self.contest_name
        problem_path = contest_path + '/' + self.problem_name + '.tests'
        tests = []
        if os.path.exists(problem_path):
            with open(problem_path, 'r') as rf:
                tests = json.load(rf)
        else:
            plm
            os.makedirs(contest_path, exist_ok=True)
            self.page = bs4.BeautifulSoup(urllib.request.urlopen(self.link), "html.parser")
            inputs = self.page.find_all('div', attrs = {'class' : 'input'})
            outputs = self.page.find_all('div', attrs = {'class' : 'output'})

            for pre_input, pre_output in zip(inputs, outputs):
                pat = r"\>(.+?)\<"

                raw_in = re.findall(pat, str(pre_input.find_all('pre')))
                raw_out = re.findall(pat, str(pre_output.find_all('pre')))

                test = {'input': [], 'output': []}
                for line in raw_in: test['input'].append(line)
                for line in raw_out: test['output'].append(line)
                tests.append(test)
            with open(problem_path, 'w') as wf:
                json.dump(tests, wf)

        return tests

class Compiler:
    def __init__(self, filename):
        """Extracts the extension of the file and returns the name of the compiler"""
        with open(EXTENSIONS_MAP) as extfile:
            self.filecheck = filename
            ext_map = json.load(extfile)
            self.compile_with = ext_map[os.path.splitext(filename)[1][1:]]['compile'].replace('FILENAME', filename)
            self.run_with = ext_map[os.path.splitext(filename)[1][1:]]['run'].replace('FILENAME', filename)

    def __parse_time(self, string):
        return string.split()[:3]

    def compile(self):
        """Compiles the file"""
        if self.compile_with != '' and os.path.isfile('_' + self.filecheck) == False:
            subprocess.call(self.compile_with.split())

    def run(self, run_input):
        """Runs the compiled file"""
        proc = subprocess.Popen(('time ' + self.run_with).split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate(run_input.encode('utf-8'))
        print('Took: ', self.__parse_time(stderr.decode('utf-8')))
        return stdout.decode('utf-8')

class Comparator:
    def __init__(self, real_output, expected_output):
        self.real_out = real_output
        self.expec_out = expected_output

    def compare(self):
        for real_line, expec_line in zip(self.real_out, self.expec_out):
            if real_line != expec_line: return False

        return True

def main():
    arguments = sys.argv
    source_name = sys.argv[sys.argv.index('--source') + 1]
    problem_link = sys.argv[sys.argv.index('--cf') + 1]

    parser = ExampleParser(problem_link)
    tests = parser.get_examples()
    compiler = Compiler(source_name)
    compiler.compile()
    for test in tests:
        pretty_input = '\n'.join(test['input'])
        real_result = compiler.run(pretty_input)
        if Comparator(real_result, '\n'.join(test['output'])).compare() != True:
            print('input: ', pretty_input)
            print('result: ', real_result)
        else: print('OK')


main()
