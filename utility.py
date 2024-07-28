

def addNotPresent(arr1, arr2):
    st = set()
    for el in arr1:
        st.add(el)
    for el in arr2:
        if not el in st:
            st.add(el)
            arr1.append(el)
    return arr1