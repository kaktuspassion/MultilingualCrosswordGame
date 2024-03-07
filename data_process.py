import pandas as pd
import random
import re
import os
from nltk.corpus import wordnet
import nltk
import ast

# nltk.download('wordnet')  # download WordNet corpora
# nltk.download('omw-1.4')  # download Open Multilingual WordNet corpora


def load_and_process(language, freq_threshold=0):
    print('Load and processing {}_CEFRLex.tsv......'.format(language))
    file_path = {
        'english': 'data/EFLLex_NLP4J.tsv',
        'spanish': 'data/ELELex_Freeling.tsv',
        'french': 'data/FLELex_TreeTagger_Beacco.tsv',
        'dutch': 'data/NT2Lex_Frog - CGN.tsv',
        'swedish': 'data/SVALex_Korp.tsv'
    }.get(language.lower())
    CEFRLex_data = pd.read_csv(file_path, sep='\t')

    relevant_columns = {
        'english': ['word', 'level_freq@a1', 'level_freq@a2', 'level_freq@b1', 'level_freq@b2', 'level_freq@c1'],
        'spanish': ['word', 'level_freq@a1', 'level_freq@a2', 'level_freq@b1', 'level_freq@b2', 'level_freq@c1'],
        'french': ['word', 'freq_A1', 'freq_A2', 'freq_B1', 'freq_B2', 'freq_C1'],
        'dutch': ['word', 'U@A1', 'U@A2', 'U@B1', 'U@B2', 'U@C1'],
        'swedish': ['word', 'level_freq@a1', 'level_freq@a2', 'level_freq@b1', 'level_freq@b2', 'level_freq@c1']
    }.get(language.lower())

    processed_data = CEFRLex_data[relevant_columns]
    cefr_levels = ['a1', 'a2', 'b1', 'b2', 'c1']

    processed_data_lst = []
    processed_clue_lst = []
    for row_idx in processed_data.index:
        word = processed_data.iloc[row_idx, 0]  # loop to process every word row by row
        if pd.isna(word):
            # if the word is NaN, skip the word (note: Swedish raw data has NaN)
            continue

        try:  # maybe a IdxError in processed_data_lst
            if word == processed_data_lst[-1][0]:
                # if it is a repeated word, skip the word
                continue
        except:
            pass

        word_freq = processed_data.iloc[row_idx, 1:].tolist()   # frequency of the word occurs in different cefr level

        if type(word_freq[0]) == str:   # turn the str into float (note: Dutch raw data has '-' in frequency)
            word_freq = [re.sub(r'-', '0', freq) for freq in word_freq]
            word_freq_digit = [float(freq) for freq in word_freq]
        else:
            word_freq_digit = word_freq

        max_freq = max(word_freq_digit)
        if (max_freq > freq_threshold and len(word) != 1
                and re.search(r'\d', word) is None and re.search(r'[-_.:]', word) is None):
            # discard words under freq_threshold, and discard one-letter words
            # discard the words including digits(0-9), or including '.', '-', '_'(Hyphenated word)
            word_cefr = cefr_levels[word_freq_digit.index(max_freq)]
            processed_data_lst.append([word, word_cefr])

            clues = generate_clue(word, language)
            if clues:    # discard words cannot find a clue
                processed_clue_lst.append([word, word_cefr, clues])

    processed_data = pd.DataFrame(processed_data_lst, columns=['WORD', 'CEFR'])
    processed_clue = pd.DataFrame(processed_clue_lst, columns=['WORD', 'CEFR', 'CLUE'])

    if not os.path.isdir('data/processed_data'):
        os.makedirs('data/processed_data')
    processed_data.to_csv('data/processed_data/{}_data.tsv'.format(language), sep='\t')  # save processed data
    processed_clue.to_csv('data/processed_data/{}_clue.tsv'.format(language), sep='\t')  # save processed data with clue
    print('Processing done!!! Files <{}_data.tsv> <{}_clue.tsv> has been saved in folder ./data/processed_data/ \n'
          .format(language, language))

    return processed_data, processed_clue


def load_processed_data(language):
    file_path = 'data/processed_data/{}_clue.tsv'.format(language)
    processed_data_fd = pd.read_csv(file_path, sep='\t')
    return processed_data_fd


def select_word_clue_list(language_data, cefr_level, num_words=20, max_clue_len=50):
    # find words corresponding to the given cefr_level
    words_cefr = language_data['CEFR'].tolist()

    # print([words_cefr.count(i) for i in ['a1', 'a2', 'b1', 'b2', 'c1']])

    target_idx = [i for i, x in enumerate(words_cefr) if x == cefr_level]
    target_words = [language_data['WORD'].tolist()[i] for i in target_idx]
    target_clues = [language_data['CLUE'].tolist()[i] for i in target_idx]

    # Randomly select words
    selected_word_clue = []
    idx = []
    while len(selected_word_clue) <= num_words:
        random_idx = random.randint(0, len(target_words)-1)
        while random_idx in idx:
            random_idx = random.randint(0, len(target_words)-1)

        selected_word = target_words[random_idx]
        selected_clues = target_clues[random_idx]

        # we need to convert the str into list, and randomly choose a clue ( clues = "['clue1', 'clue2', ....]" )
        selected_clues_list = ast.literal_eval(selected_clues)
        select_clue = random.sample(selected_clues_list, 1)[0]  # random choose a clue among all clues

        if len(select_clue) > max_clue_len:
            continue
        else:
            selected_word_clue.append([selected_word, select_clue])
            idx.append(random_idx)

    return selected_word_clue


def generate_clue(word, language):
    target_lang = {
        'english': 'eng',
        'spanish': 'spa',
        'french': 'fra',
        'dutch': 'nld',
        'swedish': 'swe'
    }.get(language.lower())  # OWM supported language

    synsets = wordnet.synsets(word, lang=target_lang)

    if synsets:
        definitions = []
        for synset in synsets:
            definitions.append(synset.definition())
        return definitions
    else:
        return None


# if __name__ == '__main__':
#     lang_data = load_processed_data('english')
#     word_list = select_word_clue_list(lang_data, 'a1', num_words=20, max_clue_len=50)
#     print([word[0] for word in word_list])
