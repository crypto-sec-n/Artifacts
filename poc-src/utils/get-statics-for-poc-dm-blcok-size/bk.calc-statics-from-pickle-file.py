import pickle, sys, base64, statistics, datetime
import matplotlib.pyplot as plt
from collections import Counter

def custom_sort_key(item):
    key, _ = item
    if key == "≥177":
        return 177
    return int(key)

a = sys.argv
if len(a)<2:
    print('Please run as; python3 calc-statics-from-pickle-file.py filename.pickle')

dm_list_all = list()
urls = []
for i in range(1, len(sys.argv)):
    filename = sys.argv[i]
    with open(filename, mode="rb") as f:
        dm_list_all += pickle.load(f)[:10000]
        urls.append(filename[len("dm-"):-len("-JST-yy-mm-dd-HH-MM-SS.pickle")])

print('dm_list_all length:%d' % len(dm_list_all))
unique_dm_list = list({dm["id"]: dm for dm in dm_list_all}.values())
unique_dm_list = sorted(unique_dm_list, key=lambda x:x['created_at'])
print('unique_dm_list length:%d' % len(unique_dm_list))

ciphertext_length_list = list()
for d in unique_dm_list:
    if not 'content' in d:
      continue
    content = d['content'].split('?iv=')
    if len(content)<2:
        continue
    c_b64, iv_b64 = content
    c = base64.b64decode(c_b64)
    ciphertext_length_list.append(len(c))
  


print('Collected DMs:%d' % len(ciphertext_length_list))
print('Max:%d' % max(ciphertext_length_list))
print('Min:%d' % min(ciphertext_length_list))
print('Avg:%d' % (sum(ciphertext_length_list)/len(ciphertext_length_list)))
print('Median:%d' % statistics.median(ciphertext_length_list))
mode_multi = [i for i in statistics.multimode(ciphertext_length_list)]
print('Mode:%s' % (" and ".join([str(i) for i in mode_multi])))


data_counts = Counter(ciphertext_length_list)

# 176より大きいアイテムと176以下のアイテムに分ける
greater_than_176 = {str(key): value for key, value in data_counts.items() if key > 176}
less_or_equal_176 = {str(key): value for key, value in data_counts.items() if key <= 176}

# 176より大きいアイテムの出現回数を合計
sum_greater_than_176 = sum(greater_than_176.values())

# 176以下のアイテムと176より大きいアイテムの合計を一つのアイテムとしてグラフに追加
final_counts = less_or_equal_176
final_counts["≥177"] = sum_greater_than_176

#final_counts = sorted(final_counts, key=lambda x:x[0])
final_counts = dict(sorted(final_counts.items(), key=lambda x: custom_sort_key(x)))


# キーと値を取り出す
final_values = list(final_counts.keys())
final_frequencies = list(final_counts.values())

# show percentage
print('%% for 1 block(16 Byte):')
print(final_counts["16"]/sum(final_frequencies)*100)

print('%% for modes:')
for i in mode_multi:
    print('%% for %d block(%d Byte):' % (i//16, i))
    print(final_counts[str(i)]/sum(final_frequencies)*100)

# 棒グラフの作成
plt.bar(final_values, final_frequencies)

latest_date = datetime.datetime.utcfromtimestamp(unique_dm_list[-1]['created_at']).strftime('%d %b, %Y')

# グラフのタイトルと軸ラベルの追加
#plt.title("Ciphertext Frequency on %s (%s)" % (",".join(urls), latest_date))
#plt.title("Ciphertext Frequency on 3 servers")
plt.xlabel("Ciphertext size~(Byte)")
plt.ylabel("Posts (DMs)")

plt.savefig("myImagePDF.pdf", format="pdf", bbox_inches="tight")
# グラフの表示
plt.show()