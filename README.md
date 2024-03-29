# pyjop
Official Python interface for JOY OF PROGRAMMING. More info about the game at https://store.steampowered.com/app/2216770

## installation
pyjop comes pre-packaged with JOY OF PROGRAMMING in a dedicated Python env. So for the default gaming experience, a manual installation is not needed.
If you wish to use use your own Python interpreter and IDE to communicate with the game, please install pyjop and its requirements in the Python environment of your choice. Please note that this disables the sandboxing normally used within the game and also prevents some gameplay (features like unlocking certain modules) from working correctly. As such, this is not recommended for the normal gaming experience, but certainly has its uses beyond that.

```python
pip install git+https://github.com/maschere/pyjop -U
```

## development
If you wish to contribute to pyjop, please feel free to fork this repo and issue pull requests. Additionally please join our Discord server to discuss potential changes.

https://discord.com/invite/2ZrdzkNeBP

## third-party programming interfaces
If you are interested in creating a differently flavored Python-wrapper for JOY OF PROGRAMMING or an interface for any other programming language, you are welcome to use this repo as reference. The most important part is re-implementing the socket communication protocol. See class [NPArray](https://github.com/maschere/pyjop/blob/main/pyjop/EntityBase.py#L45) as the starting point. Feel free to mention and discuss these projects on our discord and I can also link to them from this section. Just let me know.