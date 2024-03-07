from data_process import load_and_process


if __name__ == '__main__':
    languages = ['english', 'spanish', 'french', 'dutch', 'swedish']
    for lang in languages:
        load_and_process(lang)
