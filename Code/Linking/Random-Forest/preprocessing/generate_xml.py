import sys
import os
import csv
import javalang

import re

from utils.command_line import CommandLineHelper


class Preprocessing():
	def __init__(self, xml_folder, output_folder, input_folder):

		self.csv_files=[f for f in os.listdir(input_folder) if ".csv" in f]
		# regex to find the comments
		self.comment_regex="[^:]//.*|/\\*((.|\\n)(?!=*/))+\\*/"

		self.comment_regex2='''/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/'''
		self.input_folder=input_folder
		self.output_folder=output_folder
		self.xml_folder=xml_folder



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

	def store_xml(self):
		'''
		create the xml files for computing code features
		'''

		for f in self.csv_files:
			dataset=f.split(".")[0]
			print(dataset)

			# if dataset != "eval":
			# 	continue

			print("PROCESSING {}".format(f))

			result_name=os.path.join(self.xml_folder, "{}.csv".format(dataset))

			import pandas as pd

			df = pd.read_csv(os.path.join(self.input_folder, f), encoding="utf-8")

			rows=list()

			indexes=list()

			for index, row in df.iterrows():
				rows.append(row)
				indexes.append(index)

			print("Read {} lines".format(len(rows)))

			istances=rows
			indexes=indexes

			result=dict()
			result_commented=dict()
			result_single_comment=dict()

			to_remove=list()

			for i, (ind, l) in enumerate(df.iterrows()):

				try:
					if i%1==0:
						print("PROCESSED {} OUT OF {}".format(i, len(istances)))

					name=str(l["index"])

					code=l["originalMethod"]

					instance=int(l["artifact_id"])
					print(instance)

					code_no_comments=re.sub(self.comment_regex, '<<COMMENT>>', code)
					code_no_comments=re.sub(self.comment_regex2, '<<COMMENT>>', code_no_comments)

					lines=code_no_comments.split("\n")

					# remove the lines that contain only the comment
					lines=[l for l in lines if l.strip()!="<<COMMENT>>"]

					# remove inline comments
					lines=[l.replace("<<COMMENT>>", "") for l in lines]

					code_start_end=l["modelOutput"]

					commented_lines=self.find_commented_lines(code_start_end, lines)
					
					if len(commented_lines)==0:
						to_remove.append(ind)
						print("SKIPPED B {}".format(name))
						continue

					path_file=os.path.join(self.output_folder, "test.java")
					file=open(path_file, 'w+')

					for line in lines:
						file.write(line+"\n")

					file.close()

					res=self.process_instance()

					if len(res)==0:
						continue

					code_single_comment=self.create_method_code_comment(code_start_end, lines)

					path_file=os.path.join(self.output_folder, "test.java")
					file=open(path_file, 'w+')

					for line in code_single_comment:
						file.write(line+"\n")

					file.close()

					res_single=self.process_instance()

					if len(res)==0:
						to_remove.append(ind)
						print("SKIPPED C {}".format(name))
						continue

					all_lines="".join(res_single)
					if "<comment" not in all_lines:
						to_remove.append(ind)
						print("SKIPPED D {}".format(name))
						continue

					result[name]=res
					result_commented[name]=commented_lines
					result_single_comment[name]=res_single
				except Exception as e:
					print("EXCEPTION {}".format(e))
					to_remove.append(ind)
			self.write_csv(result, result_commented, result_single_comment, result_name)
		
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

	def find_commented_lines(self, code_start_end, original_lines):

		code=code_start_end.split("<comment>")
		
		res=list()
		for l in code:
			if "</comment>" not in l:
				res.append(l)
			else:
				res.append("<<COMMENT>>")
				res.append(l.split("</comment>")[1])

		code="".join(res)

		code_no_comments=re.sub(self.comment_regex, '<<COMMENT>>', code)
		code_no_comments=re.sub(self.comment_regex2, '<<COMMENT>>', code_no_comments)

		lines=code_no_comments.split("\n")

		# remove the lines that contain only the comment
		lines=[l for l in lines if l.strip()!="<<COMMENT>>"]

		# remove inline comments
		lines=[l.replace("<<COMMENT>>", "") for l in lines]

		all_lines=(("{*&^%}".join(lines)).replace("<start>","").replace("<end>",""))
		formatted_lines=all_lines.split("{*&^%}")

		result=self.check_correctess(original_lines, formatted_lines)

		if result==True:
			commented_lines=self.find_referenced_lines(lines)
			return commented_lines

		return list()


	def create_method_code_comment(self, code_start_end, original_lines):
		'''
		we only keep the last comment. We don't need the comment text so we add a random
		commit message. This is needed for code_comment features (we need to count the number
		of statements between the (last) comment and each statement)
		'''

		code=code_start_end.replace("<start>","").replace("<end>","")

		code=code.split("<comment>")
		
		num_blocks=len(code)

		res=list()
		for i, l in enumerate(code):
			if "</comment>" not in l:
				res.append(l)
			else:
				if i!=num_blocks-1:
					res.append("<<COMMENT>>")
					res.append(l.split("</comment>")[1])
				else:
					res.append("<<AA>>")
					res.append(l.split("</comment>")[1])


		code="".join(res)

		code_no_comments=re.sub(self.comment_regex, '<<COMMENT>>', code)
		code_no_comments=re.sub(self.comment_regex2, '<<COMMENT>>', code_no_comments)

		# we want to be sure that the comment is on a single line (i.e., the line of the comment involves only the comment)
		# if this is not true, we add an extra new line before and after

		to_replace=""

		# used to check the correct splitting

		parts=code_no_comments.split("<<AA>>")

		if parts[0].replace(" ", "")[-1]!="\n":
			to_replace="\n"
		to_replace+="<<AA>>"
		if parts[1].replace(" ", "")[0]!="\n":
			to_replace+="\n"

		code_no_comments=code_no_comments.replace("<<AA>>", to_replace)

		code_single_comment=code_no_comments.replace("<<AA>>", "//test")

		lines=code_single_comment.split("\n")

		# remove the lines that contain only the comment
		lines=[l for l in lines if l.strip()!="<<COMMENT>>"]

		# remove inline comments
		lines=[l.replace("<<COMMENT>>", "") for l in lines]

		all_lines=(("{*&^%}".join(lines)))
		formatted_lines=all_lines.split("{*&^%}")

		# for l in formatted_lines:
		# 	print(l)

		return formatted_lines



	def check_correctess(self, lines_old, lines_new):
		'''
		check if we correctly processed the data (i.e., the lines are exactly the same)
		'''
		if len(lines_old) != len(lines_new):
			for x,y in zip(lines_old, lines_new):
				print("{} --- {}".format(x,y))
			print(len(lines_old), len(lines_new))
			return False

		for x,y in zip(lines_old, lines_new):
			# print("{} --- {}".format(x,y))
			if x.replace(" ","").replace("\r","").replace("\n","").replace("\t","") != y.replace(" ","").replace("\r","").replace("\n","").replace("\t",""):
				return False

		return True


	def find_referenced_lines(self, lines):
		'''
		find the lines that the comment is describing
		'''
		commented_lines=list()
		is_commented=False
		for i, l in enumerate(lines):
			if "<start>" in l:
				is_commented=True
			if is_commented:
				commented_lines.append(i+1)
			if "<end>" in l:
				is_commented=False

		return commented_lines

# store_xml()