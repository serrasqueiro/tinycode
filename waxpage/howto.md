# waxpage - Wax your pages

Python package.
The `waxpage` package allows better readability of text files.

## redit

Do `import waxpage.redit as redit` and enjoy its functions.


## dumper

dumper.py shows latin-1 text from UTF-8.

Consider the following pangrams:

- portuguese
> � noite, vov� Kowalsky v� o im� cair no p� do ping�im queixoso e vov� p�e a��car no ch� de t�maras do jabuti feliz (no pa�s).

  + means:
  > > At night, Grandpa Kowalsky sees the imam fall at the foot of the plaintive penguin and Grandma puts sugar in the date tea of the happy tortoise (at his country).

```
python3 dumper.py --simple --try-latin-1 howto.md | grep ^">"
```

