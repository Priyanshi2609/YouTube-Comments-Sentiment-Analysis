import pandas
from pprint import pprint
class OnlyComments():
    def extract_only_comments(self,file):
        data = pandas.read_csv(file)
        list_of_comments = data["Comment"].to_list()

# print(list_of_comments)
        originalText = {
        "Comment": list_of_comments
    }
        # print(originalText)
        new_df = pandas.DataFrame(originalText)
        extracted_data_path = "extracted_comments_new.csv"
        new_df.to_csv(extracted_data_path)
