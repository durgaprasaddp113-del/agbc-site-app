import os
app = open('src/App.js', encoding='utf-8').read()
us = app.find('function useStore() {')
print("useStore start:")
print(app[us:us+150])
ret = app.rfind('return {', us, us+9000)
print("---RETURN---")
print(app[ret:ret+300])
input("Press Enter...")
