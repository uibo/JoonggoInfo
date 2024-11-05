# df1 = df.groupby("upload_date").sum()
# df1["count"] = df.groupby("upload_date").count()
# current_date = (df1.iloc[0].name) + datetime.timedelta(days=4)
# end_date = df1.iloc[((df1["price"].count())-1)].name

# mvl_dict = dict()
# volumn_dict = dict()
# while current_date <= end_date:
#     date_list = [current_date - datetime.timedelta(days=4),
#                     current_date - datetime.timedelta(days=3),
#                     current_date - datetime.timedelta(days=2),
#                     current_date - datetime.timedelta(days=1),
#                     current_date]
#     existing_date = df1[df1.index.isin(date_list)]
#     if not existing_date.empty:
#         volume = int(existing_date["count"].sum())
#         mvl = int(existing_date["price"].sum()/volume)
#     else:
#         mvl = 0
#         volume = 0
#     mvl_dict[date_list[4].strftime("%Y-%m-%d")] = mvl
#     volumn_dict[date_list[4].strftime("%Y-%m-%d")] = volume
#     current_date += datetime.timedelta(days=1)
# print(mvl_dict, volumn_dict)