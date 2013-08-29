from pymarkovchain import MarkovChain
from json import load
from re import compile as rc, escape, sub
from sys import argv
from os.path import join, dirname
from string import punctuation
from optparse import OptionParser
from pkg_resources import resource_filename


defaults = {'filename': "%s/static/listicles.json" % dirname(__file__),
            'output': "%s/static/tweets.txt" % dirname(__file__),
            'seed': False}


def build_parser():
    parser = OptionParser()
    parser.add_option("-f", "--file",
                      dest="filename",
                      default=defaults['filename'])
    parser.add_option("-o", "--output",
                      dest="output",
                      default=defaults['output'])
    parser.add_option("-s", "--seed",
                      dest="seed",
                      default=False)
    return parser


class BuzzFeeder(object):

    def __init__(self, **kwargs):
        self.chain = MarkovChain("%s/static/markov" % dirname(__file__))
        self.proceed = True
        for k, v in kwargs.items():
            if not k in defaults:
                raise ValueError
            setattr(self, k, kwargs.get(v, defaults[k]))
        with open(self.filename) as f:
            self.data = load(f)
        if not getattr(self, 'seed'):
            self.seed = False

    @property
    def titles(self):
        return map(lambda x: d['title'], filter(lambda y: y,
                                                self.data))

    @property
    def text(self):
        return rc(r'[%s]' % escape(punctuation)) \
            .sub(" b", "\n".join(self.titles).lower())

    def generate_database(self):
        self.chain.generateDatabase(self.text)

    def ask(self, prompt, opts=[]):
        prompt = ">>>  " + prompt
        if opts:
            prompt += " [%s]" % "|".join(opts)
        response = raw_input(prompt).lower()
        if 'x' in response:
            self.proceed = False
            return self.proceed
        if opts and response not in opts:
            raise ValueError
        return response

    def prompt(self, candidate):
        print ">>> '%s'" % candidate
        if not self.proceed:
            return False
        q = self.ask("Tweet this text?", opts=['y', 'n'])
        if not q:
            return False
        if 'y' in q:
            return candidate
        if 'n' in q:
            if 'y' in self.ask("Edit this text?", opts=['y', 'n']):
                return self.ask("Enter edited text: ")
            else:
                return True

    def generate(self):
        if not self.seed:
            yielder = self.chain.generateString
        else:
            yielder = self.chain.generateStringWithSeed
        yargs = [] if not self.seed else [self.seed]
        while self.proceed:
            yield yielder(*yargs) \
                .split(".py")[-1] \
                .strip() \
                .title()

    def run(self):
        print "[ press X to stop at any time ]"
        with open(self.output, "a") as tweets:
            for candidate in self.generate():
                response = self.prompt(candidate)
                if not response:
                    break
                if not isinstance(response, bool):
                    tweets.write(response.encode('ascii', 'ignore'))
                    tweets.write('\n')
                print ''


def main(*args, **kwargs):
    options, args = build_parser().parse_args()
    params = filter(lambda x: getattr(options, x),
                    defaults)
    kwargs = {k: defaults[k] for k in params}
    for k, v in defaults.items():
        if k not in kwargs:
            kwargs[k] = v
    feeder = BuzzFeeder(**kwargs)
    feeder.run()


if __name__ == "__main__":
    main()
