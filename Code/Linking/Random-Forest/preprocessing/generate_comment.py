import sys
import os
import csv
import javalang

import re

from utils.command_line import CommandLineHelper

from lxml import etree as ET

class PreprocessingComment():
    def __init__(self, xml_folder, output_folder, input_folder):
        self.csv_files = [f for f in os.listdir(input_folder) if ".csv" in f]
        # regex to find the comments
        self.comment_regex = "[^:]//.*|/\\*((.|\\n)(?!=*/))+\\*/"

        self.comment_regex2 = '''/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/'''
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.xml_folder = xml_folder


    def write_csv(self, dict_data, dict_commented, dict_single_comment, name_file):
        header = ['id', 'xml', 'referenced_lines', 'xml_single_comment']

        with open(name_file, 'w', encoding='UTF8') as f:
            writer = csv.writer(f)

            # write the header
            writer.writerow(header)

            for k in dict_data.keys():
                xml=dict_data[k]
                lines=dict_commented[k]
                xml_single_comment=dict_single_comment[k]
                data=list()
                data.append(str(k))
                data.append(str(xml))
                data.append(str(lines))
                data.append(str(xml_single_comment))

                # write the data
                writer.writerow(data)

    def get_text(self, elem):

        text = ET.tostring(elem, encoding='utf8', method='text').decode("utf-8")

        lines = text.split("\n")
        start_line = 0
        end_line = 0
        for i, l in enumerate(lines):
            if len(l.strip()) > 0:
                start_line = i
                break

        for i in range(len(lines) - 1, -1, -1):
            if len(lines[i].strip()) > 0:
                end_line = i
                break

        return "\n".join(lines[start_line:end_line + 1])

    def store_comment_info(self):
        '''
        create the xml files for computing code features
        '''

        f="test.csv"

        import pandas as pd

        df = pd.read_csv(os.path.join(self.input_folder, f), encoding="utf-8")

        print("Read {} lines".format(len(df.index)))

        dict_result=dict()

        for i, (ind, l) in enumerate(df.iterrows()):

            try:
                if i%1==0:
                    print("PROCESSED {} OUT OF {}".format(i, len(df.index)))

                # if i<2800:
                #   continue

                name=str(l["index"])
                print(name)

                # if int(name)> 200:
                #     sys.exit(0)

                code=l["originalMethod"]

                instance=int(l["artifact_id"])
                # print(instance)

                lines=code.split("\n")

                path_file=os.path.join(self.output_folder, "test.java")
                file=open(path_file, 'w+')

                for line in lines:
                    file.write(line+"\n")

                file.close()

                xml_lines=self.process_instance()

                # print(xml_lines)

                xml = bytes(bytearray("\n".join(xml_lines), encoding='utf-8'))
                tree = ET.XML(xml)

                commented_lines=list()

                for elem in tree.iter():
                    # print(elem.tag)

                    if "comment" in elem.tag:

                        # num_lines=len(elem.text.split("\n"))
                        # print(num_lines)
                        num_new_lines=(elem.text.count("\n"))
                        # print(num_new_lines)



                        text=""
                        for i in range(num_new_lines):
                            text+="\n"

                        elem.text = text
                        start=-1
                        end=-1
                        for attrib in elem.attrib:

                            if "start" in attrib:
                                start=int((elem.attrib[attrib]).split(":")[0])
                            if "end" in attrib:
                                end=int((elem.attrib[attrib]).split(":")[0])
                        # print(start, end)
                        for i in range(start, end+1):
                            commented_lines.append(i)

                commented_lines=list(set(commented_lines))
                commented_lines.sort()
                # print(commented_lines)
                # if name=="1808":
                #     sys.exit(0)



                # print(commented_lines)

                code=self.get_text(tree)
                # print(code)
                lines=code.split("\n")
                print(lines)


                # we remove the commented lines if there is something written on the same line
                commented_lines_ok=list()
                for c in commented_lines:
                    if len(lines[c-1].strip())==0:
                        commented_lines_ok.append(c)

                dict_result[name]=str(commented_lines_ok)

                # sys.exit(0)


            except Exception as e:
                print("EXCEPTION {}".format(e))

        f=open(os.path.join(self.input_folder, "commented_lines.txt"), "w+")

        f.write(str(dict_result))

        f.close()

        # write_csv(result, result_commented, result_single_comment, result_name)
        # print(to_remove)
        # df_train = df.drop(to_remove)
        # df_train.to_csv('{}.csv'.format(dataset), index=False)


    def process_instance(self):
        '''
        use srcml for checking the correctness of the method
        '''
        path_file="test.java"
        c=CommandLineHelper()

        cmd="srcml --position {} -o {}.xml".format(path_file,path_file)

        c.exec_command(cmd, self.output_folder)

        res, lines=self.check_instances(os.path.join(self.output_folder, "{}.xml".format(path_file)))
        if not res:
            return list()

        return lines


    def check_instances(self, file_path):
        file=open(file_path, "r")

        lines = file.readlines()
        lines=[l.strip() for l in lines]

        file.close()

        if len(lines)<3:
            return False, lines
        return True, lines

