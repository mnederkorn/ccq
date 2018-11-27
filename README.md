# ccq
Computation of minimal conjunctive queries via core graph computation

## Installation:

This tool is based on coresh.py from: [CoReS](https://github.com/mnederkorn/CoReS)
To run ccq you need to make coresh.py available in your python context. The easiest way to do this, is by putting ccq.py in the same folder as coresh.py.

## Usage:

To run ccq with a GUI, just start it without any parameters.

If you want solve a problem instance via CLI, you can pass the conjunctive query as a string, e.g.:  
```python .\ccq.py "(x).(y,u,v).(R(x,y),R(x,b),R(a,b),R(u,c),R(u,v),S(a,c,d))"```

The input format for both the GUI and CLI mode is as follows:  
```(X).(Y).(A)```  
Where X, Y and A are comma-seperated lists representing in order:
Unbound variables, bound variables and atomic formulae.
Variables and predicates are named according to regex ```[a-zA-Z0-9]+```.
Formulae are written as: A(V), where A is the predicate identifier and
V is a comma-seperated list of variables.
All variables in a formula which are not explicitly listed in X and Y are
implicitly interpreted as constants.
