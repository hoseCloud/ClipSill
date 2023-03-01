import kss
from collections import Counter
from time import sleep
from numpy import dot
from numpy.linalg import norm
from konlpy.tag import Okt
okt = Okt()

class Textrank:
    def __init__(self, summary_length, sentence_list, sock):
        self.summary_length = summary_length
        self.sentence_list = sentence_list
        self.sentence_word = []
        self.wordset = set()
        self.graph_matrix = []
        self.node_weight = []

        #print("Converting String To Sentences...")
        sock.sendall("[6/10] Converting String To Sentences...".encode())
        self.__make_string_to_sentences()
        sleep(0.3)

        #print("Making Tuple...")
        sock.sendall("[7/10] Making Tuple...".encode())
        self.__make_word_tuple()
        sleep(0.3)

        #print("Making Graph Matrix...")
        sock.sendall("[8/10] Making Graph Matrix...".encode())
        self.__make_graph_matrix()
        sleep(0.3)

        #print("Making Graph Weight...")
        sock.sendall("[9/10] Making Graph Weight...".encode())
        self.__make_graph_weight()
        sleep(0.3)

        #print("Sorting Matrix...") 
        sock.sendall("[10/10] Sorting Matrix...".encode()) 
        self.__sort_matrix()
        sleep(0.3)
    
    def __make_string_to_sentences(self):
        self.sentence_list.replace('\n','')
        self.sentence_list = kss.split_sentences(self.sentence_list)

    def __make_word_tuple(self):
        for sentence in self.sentence_list:
            tmp_nouns = okt.nouns(sentence)
            self.wordset = self.wordset.union(set(tmp_nouns))
            self.sentence_word.append(tuple(tmp_nouns))
    
    def __make_graph_matrix(self):
        for words in self.sentence_word:
            tmp_list = []
            tmp_words_counter = Counter(words)

            for matrix_word in list(self.wordset):
                if  matrix_word in words:
                    tmp_list.append(tmp_words_counter[matrix_word])
                else:
                    tmp_list.append(0)

            self.graph_matrix.append(tmp_list)

    def __make_graph_weight(self):
        index = 0

        for matrix_element1 in self.graph_matrix:
            weight = 0
            for matrix_element2 in self.graph_matrix:
                if norm(matrix_element1)*norm(matrix_element2) == 0:
                    weight -= 1
                else:
                    weight += dot(matrix_element1, matrix_element2)/(norm(matrix_element1)*norm(matrix_element2))

            self.node_weight.append({'weight': weight, 'index': index})
            index += 1

    def __sort_matrix(self):
        self.node_weight = sorted(self.node_weight, key=lambda x: x['weight'], reverse=True)

    def summarize(self):
        tmp_list = []
        return_sentences = []
        for count in range(self.summary_length):
            tmp_list.append(self.node_weight[count])

        tmp_list = sorted(tmp_list, key=lambda x: x['index'])

        for tmp in tmp_list:
            return_sentences.append(self.sentence_list[tmp['index']])

        return return_sentences

if __name__ == '__main__':
    my_string1 = open('./output_1.txt', 'r').read()
    textrank = Textrank(3, my_string1)
    for s in textrank.summarize():
        print(s)
