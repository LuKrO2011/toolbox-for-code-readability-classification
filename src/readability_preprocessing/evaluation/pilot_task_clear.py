import matplotlib.pyplot as plt

ratings = {
    "1": 1,
    "2": 1,
    "3": 0,
    "4": 5,
    "5": 3
}


def generate_bar_chart(data):
    keys = list(data.keys())
    values = list(data.values())

    plt.bar(keys, values)
    plt.xlabel('Rating')
    plt.ylabel('Count')
    plt.show()


generate_bar_chart(ratings)
