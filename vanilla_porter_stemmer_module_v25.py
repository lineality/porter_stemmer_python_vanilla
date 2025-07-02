#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import os
import sys
import traceback
from typing import List  # , Optional, Union

"""
################################
# vanilla porter stemmer module
################################

Porter Stemming!!

This is a production-oriented python module for Martin Porter's classic
and eternal, and lovely, and elegant, Porter Stemmer,
designed to be:
- easily deployed (in projects, serverless endpoints, etc.)
- no 3rd party dependencies or non-'standard libraries' required
- can be imported as a class into other python code
- can be used from CLI or called from the .py form as a
     python script for terminal applications
- handles:
    - individual words
    - documents as strings
    - documents as files
    - output a stemmatized string
    - output a stem-token-list
- allows removal of non-alphanumeric characters
- allows original and NLTK modes
- allows 'lower-case' or 'preserve-case' modes
- should contain comprehensive tests
- should contain comprehensive demo
- should be error handling
- should give example of use
- has a --help parameter

See:
https://tartarus.org/martin/PorterVanillaPyStemmer/

This NLTK version has various hidden third party dependency element:
https://www.nltk.org/_modules/nltk/stem/porter.html#PorterVanillaPyStemmer

This old python version is not current python and take file-input.
by Vivake Gupta    	   	Jan 2001  
https://tartarus.org/martin/PorterVanillaPyStemmer/python.txt

Martin Porter's ansi-c threadsafe version here:
https://tartarus.org/martin/PorterVanillaPyStemmer/c_thread_safe.txt


Classes:
    PorterVanillaPyStemmer: Main class implementing the Porter Stemming Algorithm

Functions:
    stem_file_wrapper: Process a text file and output stemmed version
    run_comprehensive_tests: Run test suite
    [other CLI functions...]

Usage:
    Command line:
        python porter_stemmer.py --word running flies
        python porter_stemmer.py --file document.txt

    As module:
        from porter_stemmer import PorterVanillaPyStemmer
        stemmer = PorterVanillaPyStemmer()
        result = stemmer.stem_word('running')

License: MIT
"""


"""
porter_stemmer.py - A vanilla Porter Stemmer implementation

This module provides a pure Python implementation of
 the Porter Stemming Algorithm,
following Martin Porter's recommended extensions.
 The implementation requires no
external dependencies beyond Python's standard library.

The Porter Stemmer reduces words to their root form by
 removing common suffixes.
For example: 'running' -> 'run', 'flies' -> 'fli', 'happily' -> 'happili'

References:
    Porter, M. "An algorithm for suffix stripping."
      Program 14.3 (1980): 130-137.
    https://www.tartarus.org/~martin/PorterVanillaPyStemmer/
"""

"""
original ansi-c threadsafe code by Martin porter
https://tartarus.org/martin/PorterVanillaPyStemmer/c_thread_safe.txt

```c
/* This is the Porter stemming algorithm, coded up as thread-safe ANSI C
   by the author.

   It may be be regarded as cononical, in that it follows the algorithm
   presented in

   Porter, 1980, An algorithm for suffix stripping, Program, Vol. 14,
   no. 3, pp 130-137,

   only differing from it at the points marked --DEPARTURE-- below.

   See also http://www.tartarus.org/~martin/PorterVanillaPyStemmer

   The algorithm as described in the paper could be exactly replicated
   by adjusting the points of DEPARTURE, but this is barely necessary,
   because (a) the points of DEPARTURE are definitely improvements, and
   (b) no encoding of the Porter stemmer I have seen is anything like
   as exact as this version, even with the points of DEPARTURE!

   You can compile it on Unix with 'gcc -O3 -o stem stem.c' after which
   'stem' takes a list of inputs and sends the stemmed equivalent to
   stdout.

   The algorithm as encoded here is particularly fast.

   Release 1: the basic non-thread safe version

   Release 2: this thread-safe version

   Release 3: 11 Apr 2013, fixes the bug noted by Matt Patenaude (see the
       basic version for details)

   Release 4: 25 Mar 2014, fixes the bug noted by Klemens Baum (see the
       basic version for details)
*/

#include <stdlib.h>  /* for malloc, free */
#include <string.h>  /* for memcmp, memmove */

/* You will probably want to move the following declarations to a central
   header file.
*/

struct stemmer;

extern struct stemmer * create_stemmer(void);
extern void free_stemmer(struct stemmer * z);

extern int stem(struct stemmer * z, char * b, int k);



/* The main part of the stemming algorithm starts here.
*/

#define TRUE 1
#define FALSE 0

/* stemmer is a structure for a few local bits of data,
*/

struct stemmer {
   char * b;       /* buffer for word to be stemmed */
   int k;          /* offset to the end of the string */
   int j;          /* a general offset into the string */
};


/* Member b is a buffer holding a word to be stemmed. The letters are in
   b[0], b[1] ... ending at b[z->k]. Member k is readjusted downwards as
   the stemming progresses. Zero termination is not in fact used in the
   algorithm.

   Note that only lower case sequences are stemmed. Forcing to lower case
   should be done before stem(...) is called.


   Typical usage is:

       struct stemmer * z = create_stemmer();
       char b[] = "pencils";
       int res = stem(z, b, 6);
           /- stem the 7 characters of b[0] to b[6]. The result, res,
              will be 5 (the 's' is removed). -/
       free_stemmer(z);
*/


extern struct stemmer * create_stemmer(void)
{
    return (struct stemmer *) malloc(sizeof(struct stemmer));
    /* assume malloc succeeds */
}

extern void free_stemmer(struct stemmer * z)
{
    free(z);
}


/* cons(z, i) is TRUE <=> b[i] is a consonant. ('b' means 'z->b', but here
   and below we drop 'z->' in comments.
*/

static int cons(struct stemmer * z, int i)
{  switch (z->b[i])
   {  case 'a': case 'e': case 'i': case 'o': case 'u': return FALSE;
      case 'y': return (i == 0) ? TRUE : !cons(z, i - 1);
      default: return TRUE;
   }
}

/* m(z) measures the number of consonant sequences between 0 and j. if c is
   a consonant sequence and v a vowel sequence, and <..> indicates arbitrary
   presence,

      <c><v>       gives 0
      <c>vc<v>     gives 1
      <c>vcvc<v>   gives 2
      <c>vcvcvc<v> gives 3
      ....
*/

static int m(struct stemmer * z)
{  int n = 0;
   int i = 0;
   int j = z->j;
   while(TRUE)
   {  if (i > j) return n;
      if (! cons(z, i)) break; i++;
   }
   i++;
   while(TRUE)
   {  while(TRUE)
      {  if (i > j) return n;
            if (cons(z, i)) break;
            i++;
      }
      i++;
      n++;
      while(TRUE)
      {  if (i > j) return n;
         if (! cons(z, i)) break;
         i++;
      }
      i++;
   }
}

/* vowelinstem(z) is TRUE <=> 0,...j contains a vowel */

static int vowelinstem(struct stemmer * z)
{
   int j = z->j;
   int i; for (i = 0; i <= j; i++) if (! cons(z, i)) return TRUE;
   return FALSE;
}

/* doublec(z, j) is TRUE <=> j,(j-1) contain a double consonant. */

static int doublec(struct stemmer * z, int j)
{
   char * b = z->b;
   if (j < 1) return FALSE;
   if (b[j] != b[j - 1]) return FALSE;
   return cons(z, j);
}

/* cvc(z, i) is TRUE <=> i-2,i-1,i has the form consonant - vowel - consonant
   and also if the second c is not w,x or y. this is used when trying to
   restore an e at the end of a short word. e.g.

      cav(e), lov(e), hop(e), crim(e), but
      snow, box, tray.

*/

static int cvc(struct stemmer * z, int i)
{  if (i < 2 || !cons(z, i) || cons(z, i - 1) || !cons(z, i - 2)) return FALSE;
   {  int ch = z->b[i];
      if (ch  == 'w' || ch == 'x' || ch == 'y') return FALSE;
   }
   return TRUE;
}

/* ends(z, s) is TRUE <=> 0,...k ends with the string s. */

static int ends(struct stemmer * z, char * s)
{  int length = s[0];
   char * b = z->b;
   int k = z->k;
   if (s[length] != b[k]) return FALSE; /* tiny speed-up */
   if (length > k + 1) return FALSE;
   if (memcmp(b + k - length + 1, s + 1, length) != 0) return FALSE;
   z->j = k-length;
   return TRUE;
}

/* setto(z, s) sets (j+1),...k to the characters in the string s, readjusting
   k. */

static void setto(struct stemmer * z, char * s)
{  int length = s[0];
   int j = z->j;
   memmove(z->b + j + 1, s + 1, length);
   z->k = j+length;
}

/* r(z, s) is used further down. */

static void r(struct stemmer * z, char * s) { if (m(z) > 0) setto(z, s); }

/* step1ab(z) gets rid of plurals and -ed or -ing. e.g.

       caresses  ->  caress
       ponies    ->  poni
       ties      ->  ti
       caress    ->  caress
       cats      ->  cat

       feed      ->  feed
       agreed    ->  agree
       disabled  ->  disable

       matting   ->  mat
       mating    ->  mate
       meeting   ->  meet
       milling   ->  mill
       messing   ->  mess

       meetings  ->  meet

*/

static void step1ab(struct stemmer * z)
{
   char * b = z->b;
   if (b[z->k] == 's')
   {  if (ends(z, "\04" "sses")) z->k -= 2; else
      if (ends(z, "\03" "ies")) setto(z, "\01" "i"); else
      if (b[z->k - 1] != 's') z->k--;
   }
   if (ends(z, "\03" "eed")) { if (m(z) > 0) z->k--; } else
   if ((ends(z, "\02" "ed") || ends(z, "\03" "ing")) && vowelinstem(z))
   {  z->k = z->j;
      if (ends(z, "\02" "at")) setto(z, "\03" "ate"); else
      if (ends(z, "\02" "bl")) setto(z, "\03" "ble"); else
      if (ends(z, "\02" "iz")) setto(z, "\03" "ize"); else
      if (doublec(z, z->k))
      {  z->k--;
         {  int ch = b[z->k];
            if (ch == 'l' || ch == 's' || ch == 'z') z->k++;
         }
      }
      else if (m(z) == 1 && cvc(z, z->k)) setto(z, "\01" "e");
   }
}

/* step1c(z) turns terminal y to i when there is another vowel in the stem. */

static void step1c(struct stemmer * z)
{
   if (ends(z, "\01" "y") && vowelinstem(z)) z->b[z->k] = 'i';
}


/* step2(z) maps double suffices to single ones. so -ization ( = -ize plus
   -ation) maps to -ize etc. note that the string before the suffix must give
   m(z) > 0. */

static void step2(struct stemmer * z) { switch (z->b[z->k-1])
{
   case 'a': if (ends(z, "\07" "ational")) { r(z, "\03" "ate"); break; }
             if (ends(z, "\06" "tional")) { r(z, "\04" "tion"); break; }
             break;
   case 'c': if (ends(z, "\04" "enci")) { r(z, "\04" "ence"); break; }
             if (ends(z, "\04" "anci")) { r(z, "\04" "ance"); break; }
             break;
   case 'e': if (ends(z, "\04" "izer")) { r(z, "\03" "ize"); break; }
             break;
   case 'l': if (ends(z, "\03" "bli")) { r(z, "\03" "ble"); break; } /*-DEPARTURE-*/

 /* To match the published algorithm, replace this line with
    case 'l': if (ends(z, "\04" "abli")) { r(z, "\04" "able"); break; } */

             if (ends(z, "\04" "alli")) { r(z, "\02" "al"); break; }
             if (ends(z, "\05" "entli")) { r(z, "\03" "ent"); break; }
             if (ends(z, "\03" "eli")) { r(z, "\01" "e"); break; }
             if (ends(z, "\05" "ousli")) { r(z, "\03" "ous"); break; }
             break;
   case 'o': if (ends(z, "\07" "ization")) { r(z, "\03" "ize"); break; }
             if (ends(z, "\05" "ation")) { r(z, "\03" "ate"); break; }
             if (ends(z, "\04" "ator")) { r(z, "\03" "ate"); break; }
             break;
   case 's': if (ends(z, "\05" "alism")) { r(z, "\02" "al"); break; }
             if (ends(z, "\07" "iveness")) { r(z, "\03" "ive"); break; }
             if (ends(z, "\07" "fulness")) { r(z, "\03" "ful"); break; }
             if (ends(z, "\07" "ousness")) { r(z, "\03" "ous"); break; }
             break;
   case 't': if (ends(z, "\05" "aliti")) { r(z, "\02" "al"); break; }
             if (ends(z, "\05" "iviti")) { r(z, "\03" "ive"); break; }
             if (ends(z, "\06" "biliti")) { r(z, "\03" "ble"); break; }
             break;
   case 'g': if (ends(z, "\04" "logi")) { r(z, "\03" "log"); break; } /*-DEPARTURE-*/

 /* To match the published algorithm, delete this line */

} }

/* step3(z) deals with -ic-, -full, -ness etc. similar strategy to step2. */

static void step3(struct stemmer * z) { switch (z->b[z->k])
{
   case 'e': if (ends(z, "\05" "icate")) { r(z, "\02" "ic"); break; }
             if (ends(z, "\05" "ative")) { r(z, "\00" ""); break; }
             if (ends(z, "\05" "alize")) { r(z, "\02" "al"); break; }
             break;
   case 'i': if (ends(z, "\05" "iciti")) { r(z, "\02" "ic"); break; }
             break;
   case 'l': if (ends(z, "\04" "ical")) { r(z, "\02" "ic"); break; }
             if (ends(z, "\03" "ful")) { r(z, "\00" ""); break; }
             break;
   case 's': if (ends(z, "\04" "ness")) { r(z, "\00" ""); break; }
             break;
} }

/* step4(z) takes off -ant, -ence etc., in context <c>vcvc<v>. */

static void step4(struct stemmer * z)
{  switch (z->b[z->k-1])
   {  case 'a': if (ends(z, "\02" "al")) break; return;
      case 'c': if (ends(z, "\04" "ance")) break;
                if (ends(z, "\04" "ence")) break; return;
      case 'e': if (ends(z, "\02" "er")) break; return;
      case 'i': if (ends(z, "\02" "ic")) break; return;
      case 'l': if (ends(z, "\04" "able")) break;
                if (ends(z, "\04" "ible")) break; return;
      case 'n': if (ends(z, "\03" "ant")) break;
                if (ends(z, "\05" "ement")) break;
                if (ends(z, "\04" "ment")) break;
                if (ends(z, "\03" "ent")) break; return;
      case 'o': if (ends(z, "\03" "ion") && z->j >= 0 && (z->b[z->j] == 's' || z->b[z->j] == 't')) break;
                if (ends(z, "\02" "ou")) break; return;
                /* takes care of -ous */
      case 's': if (ends(z, "\03" "ism")) break; return;
      case 't': if (ends(z, "\03" "ate")) break;
                if (ends(z, "\03" "iti")) break; return;
      case 'u': if (ends(z, "\03" "ous")) break; return;
      case 'v': if (ends(z, "\03" "ive")) break; return;
      case 'z': if (ends(z, "\03" "ize")) break; return;
      default: return;
   }
   if (m(z) > 1) z->k = z->j;
}

/* step5(z) removes a final -e if m(z) > 1, and changes -ll to -l if
   m(z) > 1. */

static void step5(struct stemmer * z)
{
   char * b = z->b;
   z->j = z->k;
   if (b[z->k] == 'e')
   {  int a = m(z);
      if (a > 1 || a == 1 && !cvc(z, z->k - 1)) z->k--;
   }
   if (b[z->k] == 'l' && doublec(z, z->k) && m(z) > 1) z->k--;
}

/* In stem(z, b, k), b is a char pointer, and the string to be stemmed is
   from b[0] to b[k] inclusive.  Possibly b[k+1] == '\0', but it is not
   important. The stemmer adjusts the characters b[0] ... b[k] and returns
   the new end-point of the string, k'. Stemming never increases word
   length, so 0 <= k' <= k.
*/

extern int stem(struct stemmer * z, char * b, int k)
{
   if (k <= 1) return k; /*-DEPARTURE-*/
   z->b = b; z->k = k; /* copy the parameters into z */

   /* With this line, strings of length 1 or 2 don't go through the
      stemming process, although no mention is made of this in the
      published algorithm. Remove the line to match the published
      algorithm. */

   step1ab(z);
   if (z->k > 0) {
      step1c(z); step2(z); step3(z); step4(z); step5(z);
   }
   return z->k;
}

/*--------------------stemmer definition ends here------------------------*/

#include <stdio.h>
#include <stdlib.h>      /* for malloc, free */
#include <ctype.h>       /* for isupper, islower, tolower */

static char * s;         /* buffer for words tobe stemmed */

#define INC 50           /* size units in which s is increased */
static int i_max = INC;  /* maximum offset in s */

#define LETTER(ch) (isupper(ch) || islower(ch))

void stemfile(struct stemmer * z, FILE * f)
{  while(TRUE)
   {  int ch = getc(f);
      if (ch == EOF) return;
      if (LETTER(ch))
      {  int i = 0;
         while(TRUE)
         {  if (i == i_max)
            {  i_max += INC;
               s = realloc(s, i_max + 1);
            }
            ch = tolower(ch); /* forces lower case */

            s[i] = ch; i++;
            ch = getc(f);
            if (!LETTER(ch)) { ungetc(ch,f); break; }
         }
         s[stem(z, s, i - 1) + 1] = 0;
         /* the previous line calls the stemmer and uses its result to
            zero-terminate the string in s */
         printf("%s",s);
      }
      else putchar(ch);
   }
}

int main(int argc, char * argv[])
{  int i;

   struct stemmer * z = create_stemmer();

   s = (char *) malloc(i_max + 1);
   for (i = 1; i < argc; i++)
   {  FILE * f = fopen(argv[i],"r");
      if (f == 0) { fprintf(stderr,"File %s not found\n",argv[i]); exit(1); }
      stemfile(z, f);
   }
   free(s);

   free_stemmer(z);

   return 0;
}
```
"""

# """ with doc-strings redacted
# NLKT code
# from https://www.nltk.org/_modules/nltk/stem/porter.html#PorterVanillaPyStemmer
# with various third party dependencies doing unknown things

# class PorterVanillaPyStemmer(StemmerI):
#     """
#     A word stemmer based on the Porter stemming algorithm.

#         Porter, M. "An algorithm for suffix stripping."
#         Program 14.3 (1980): 130-137.

#     See https://www.tartarus.org/~martin/PorterVanillaPyStemmer/ for the homepage
#     of the algorithm.

#     Martin Porter has endorsed several modifications to the Porter
#     algorithm since writing his original paper, and those extensions are
#     included in the implementations on his website. Additionally, others
#     have proposed further improvements to the algorithm, including NLTK
#     contributors. There are thus three modes that can be selected by
#     passing the appropriate constant to the class constructor's `mode`
#     attribute:

#     - PorterVanillaPyStemmer.ORIGINAL_ALGORITHM

#         An implementation that is faithful to the original paper.

#         Note that Martin Porter has deprecated this version of the
#         algorithm. Martin distributes implementations of the Porter
#         Stemmer in many languages, hosted at:

#         https://www.tartarus.org/~martin/PorterVanillaPyStemmer/

#         and all of these implementations include his extensions. He
#         strongly recommends against using the original, published
#         version of the algorithm; only use this mode if you clearly
#         understand why you are choosing to do so.

#     - PorterVanillaPyStemmer.MARTIN_EXTENSIONS

#         An implementation that only uses the modifications to the
#         algorithm that are included in the implementations on Martin
#         Porter's website. He has declared Porter frozen, so the
#         behaviour of those implementations should never change.

#     - PorterVanillaPyStemmer.NLTK_EXTENSIONS (default)

#         An implementation that includes further improvements devised by
#         NLTK contributors or taken from other modified implementations
#         found on the web.

#     For the best stemming, you should use the default NLTK_EXTENSIONS
#     version. However, if you need to get the same results as either the
#     original algorithm or one of Martin Porter's hosted versions for
#     compatibility with an existing implementation or dataset, you can use
#     one of the other modes instead.
#     """

#     # Modes the Stemmer can be instantiated in
#     NLTK_EXTENSIONS = "NLTK_EXTENSIONS"
#     MARTIN_EXTENSIONS = "MARTIN_EXTENSIONS"
#     ORIGINAL_ALGORITHM = "ORIGINAL_ALGORITHM"


# [docs]

#     def __init__(self, mode=NLTK_EXTENSIONS):
#         if mode not in (
#             self.NLTK_EXTENSIONS,
#             self.MARTIN_EXTENSIONS,
#             self.ORIGINAL_ALGORITHM,
#         ):
#             raise ValueError(
#                 "Mode must be one of PorterVanillaPyStemmer.NLTK_EXTENSIONS, "
#                 "PorterVanillaPyStemmer.MARTIN_EXTENSIONS, or "
#                 "PorterVanillaPyStemmer.ORIGINAL_ALGORITHM"
#             )

#         self.mode = mode

#         if self.mode == self.NLTK_EXTENSIONS:
#             # This is a table of irregular forms. It is quite short,
#             # but still reflects the errors actually drawn to Martin
#             # Porter's attention over a 20 year period!
#             irregular_forms = {
#                 "sky": ["sky", "skies"],
#                 "die": ["dying"],
#                 "lie": ["lying"],
#                 "tie": ["tying"],
#                 "news": ["news"],
#                 "inning": ["innings", "inning"],
#                 "outing": ["outings", "outing"],
#                 "canning": ["cannings", "canning"],
#                 "howe": ["howe"],
#                 "proceed": ["proceed"],
#                 "exceed": ["exceed"],
#                 "succeed": ["succeed"],
#             }

#             self.pool = {}
#             for key in irregular_forms:
#                 for val in irregular_forms[key]:
#                     self.pool[val] = key

#         self.vowels = frozenset(["a", "e", "i", "o", "u"])


#     def _is_consonant(self, word, i):
#         """Returns True if word[i] is a consonant, False otherwise

#         A consonant is defined in the paper as follows:

#             A consonant in a word is a letter other than A, E, I, O or
#             U, and other than Y preceded by a consonant. (The fact that
#             the term `consonant' is defined to some extent in terms of
#             itself does not make it ambiguous.) So in TOY the consonants
#             are T and Y, and in SYZYGY they are S, Z and G. If a letter
#             is not a consonant it is a vowel.
#         """
#         if word[i] in self.vowels:
#             return False
#         if word[i] == "y":
#             if i == 0:
#                 return True
#             else:
#                 return not self._is_consonant(word, i - 1)
#         return True

#     def _measure(self, stem):
#         r"""Returns the 'measure' of stem, per definition in the paper

#         From the paper:

#             A consonant will be denoted by c, a vowel by v. A list
#             ccc... of length greater than 0 will be denoted by C, and a
#             list vvv... of length greater than 0 will be denoted by V.
#             Any word, or part of a word, therefore has one of the four
#             forms:

#                 CVCV ... C
#                 CVCV ... V
#                 VCVC ... C
#                 VCVC ... V

#             These may all be represented by the single form

#                 [C]VCVC ... [V]

#             where the square brackets denote arbitrary presence of their
#             contents. Using (VC){m} to denote VC repeated m times, this
#             may again be written as

#                 [C](VC){m}[V].

#             m will be called the \measure\ of any word or word part when
#             represented in this form. The case m = 0 covers the null
#             word. Here are some examples:

#                 m=0    TR,  EE,  TREE,  Y,  BY.
#                 m=1    TROUBLE,  OATS,  TREES,  IVY.
#                 m=2    TROUBLES,  PRIVATE,  OATEN,  ORRERY.
#         """
#         cv_sequence = ""

#         # Construct a string of 'c's and 'v's representing whether each
#         # character in `stem` is a consonant or a vowel.
#         # e.g. 'falafel' becomes 'cvcvcvc',
#         #      'architecture' becomes 'vcccvcvccvcv'
#         for i in range(len(stem)):
#             if self._is_consonant(stem, i):
#                 cv_sequence += "c"
#             else:
#                 cv_sequence += "v"

#         # Count the number of 'vc' occurrences, which is equivalent to
#         # the number of 'VC' occurrences in Porter's reduced form in the
#         # docstring above, which is in turn equivalent to `m`
#         return cv_sequence.count("vc")

#     def _has_positive_measure(self, stem):
#         return self._measure(stem) > 0

#     def _contains_vowel(self, stem):
#         """Returns True if stem contains a vowel, else False"""
#         for i in range(len(stem)):
#             if not self._is_consonant(stem, i):
#                 return True
#         return False

#     def _ends_double_consonant(self, word):
#         """Implements condition *d from the paper

#         Returns True if word ends with a double consonant
#         """
#         return (
#             len(word) >= 2
#             and word[-1] == word[-2]
#             and self._is_consonant(word, len(word) - 1)
#         )

#     def _ends_cvc(self, word):
#         """Implements condition *o from the paper

#         From the paper:

#             *o  - the stem ends cvc, where the second c is not W, X or Y
#                   (e.g. -WIL, -HOP).
#         """
#         return (
#             len(word) >= 3
#             and self._is_consonant(word, len(word) - 3)
#             and not self._is_consonant(word, len(word) - 2)
#             and self._is_consonant(word, len(word) - 1)
#             and word[-1] not in ("w", "x", "y")
#         ) or (
#             self.mode == self.NLTK_EXTENSIONS
#             and len(word) == 2
#             and not self._is_consonant(word, 0)
#             and self._is_consonant(word, 1)
#         )

#     def _replace_suffix(self, word, suffix, replacement):
#         """Replaces `suffix` of `word` with `replacement"""
#         assert word.endswith(suffix), "Given word doesn't end with given suffix"
#         if suffix == "":
#             return word + replacement
#         else:
#             return word[: -len(suffix)] + replacement

#     def _apply_rule_list(self, word, rules):
#         """Applies the first applicable suffix-removal rule to the word

#         Takes a word and a list of suffix-removal rules represented as
#         3-tuples, with the first element being the suffix to remove,
#         the second element being the string to replace it with, and the
#         final element being the condition for the rule to be applicable,
#         or None if the rule is unconditional.
#         """
#         for rule in rules:
#             suffix, replacement, condition = rule
#             if suffix == "*d" and self._ends_double_consonant(word):
#                 stem = word[:-2]
#                 if condition is None or condition(stem):
#                     return stem + replacement
#                 else:
#                     # Don't try any further rules
#                     return word
#             if word.endswith(suffix):
#                 stem = self._replace_suffix(word, suffix, "")
#                 if condition is None or condition(stem):
#                     return stem + replacement
#                 else:
#                     # Don't try any further rules
#                     return word

#         return word

#     def _step1a(self, word):
#         """Implements Step 1a from "An algorithm for suffix stripping"

#         From the paper:

#             SSES -> SS                         caresses  ->  caress
#             IES  -> I                          ponies    ->  poni
#                                                ties      ->  ti
#             SS   -> SS                         caress    ->  caress
#             S    ->                            cats      ->  cat
#         """
#         # this NLTK-only rule extends the original algorithm, so
#         # that 'flies'->'fli' but 'dies'->'die' etc
#         if self.mode == self.NLTK_EXTENSIONS:
#             if word.endswith("ies") and len(word) == 4:
#                 return self._replace_suffix(word, "ies", "ie")

#         return self._apply_rule_list(
#             word,
#             [
#                 ("sses", "ss", None),  # SSES -> SS
#                 ("ies", "i", None),  # IES  -> I
#                 ("ss", "ss", None),  # SS   -> SS
#                 ("s", "", None),  # S    ->
#             ],
#         )

#     def _step1b(self, word):
#         """Implements Step 1b from "An algorithm for suffix stripping"

#         From the paper:

#             (m>0) EED -> EE                    feed      ->  feed
#                                                agreed    ->  agree
#             (*v*) ED  ->                       plastered ->  plaster
#                                                bled      ->  bled
#             (*v*) ING ->                       motoring  ->  motor
#                                                sing      ->  sing

#         If the second or third of the rules in Step 1b is successful,
#         the following is done:

#             AT -> ATE                       conflat(ed)  ->  conflate
#             BL -> BLE                       troubl(ed)   ->  trouble
#             IZ -> IZE                       siz(ed)      ->  size
#             (*d and not (*L or *S or *Z))
#                -> single letter
#                                             hopp(ing)    ->  hop
#                                             tann(ed)     ->  tan
#                                             fall(ing)    ->  fall
#                                             hiss(ing)    ->  hiss
#                                             fizz(ed)     ->  fizz
#             (m=1 and *o) -> E               fail(ing)    ->  fail
#                                             fil(ing)     ->  file

#         The rule to map to a single letter causes the removal of one of
#         the double letter pair. The -E is put back on -AT, -BL and -IZ,
#         so that the suffixes -ATE, -BLE and -IZE can be recognised
#         later. This E may be removed in step 4.
#         """
#         # this NLTK-only block extends the original algorithm, so that
#         # 'spied'->'spi' but 'died'->'die' etc
#         if self.mode == self.NLTK_EXTENSIONS:
#             if word.endswith("ied"):
#                 if len(word) == 4:
#                     return self._replace_suffix(word, "ied", "ie")
#                 else:
#                     return self._replace_suffix(word, "ied", "i")

#         # (m>0) EED -> EE
#         if word.endswith("eed"):
#             stem = self._replace_suffix(word, "eed", "")
#             if self._measure(stem) > 0:
#                 return stem + "ee"
#             else:
#                 return word

#         rule_2_or_3_succeeded = False

#         for suffix in ["ed", "ing"]:
#             if word.endswith(suffix):
#                 intermediate_stem = self._replace_suffix(word, suffix, "")
#                 if self._contains_vowel(intermediate_stem):
#                     rule_2_or_3_succeeded = True
#                     break

#         if not rule_2_or_3_succeeded:
#             return word

#         return self._apply_rule_list(
#             intermediate_stem,
#             [
#                 ("at", "ate", None),  # AT -> ATE
#                 ("bl", "ble", None),  # BL -> BLE
#                 ("iz", "ize", None),  # IZ -> IZE
#                 # (*d and not (*L or *S or *Z))
#                 # -> single letter
#                 (
#                     "*d",
#                     intermediate_stem[-1],
#                     lambda stem: intermediate_stem[-1] not in ("l", "s", "z"),
#                 ),
#                 # (m=1 and *o) -> E
#                 (
#                     "",
#                     "e",
#                     lambda stem: (self._measure(stem) == 1 and self._ends_cvc(stem)),
#                 ),
#             ],
#         )

#     def _step1c(self, word):
#         """Implements Step 1c from "An algorithm for suffix stripping"

#         From the paper:

#         Step 1c

#             (*v*) Y -> I                    happy        ->  happi
#                                             sky          ->  sky
#         """

#         def nltk_condition(stem):
#             """
#             This has been modified from the original Porter algorithm so
#             that y->i is only done when y is preceded by a consonant,
#             but not if the stem is only a single consonant, i.e.

#                (*c and not c) Y -> I

#             So 'happy' -> 'happi', but
#                'enjoy' -> 'enjoy'  etc

#             This is a much better rule. Formerly 'enjoy'->'enjoi' and
#             'enjoyment'->'enjoy'. Step 1c is perhaps done too soon; but
#             with this modification that no longer really matters.

#             Also, the removal of the contains_vowel(z) condition means
#             that 'spy', 'fly', 'try' ... stem to 'spi', 'fli', 'tri' and
#             conflate with 'spied', 'tried', 'flies' ...
#             """
#             return len(stem) > 1 and self._is_consonant(stem, len(stem) - 1)

#         def original_condition(stem):
#             return self._contains_vowel(stem)

#         return self._apply_rule_list(
#             word,
#             [
#                 (
#                     "y",
#                     "i",
#                     (
#                         nltk_condition
#                         if self.mode == self.NLTK_EXTENSIONS
#                         else original_condition
#                     ),
#                 )
#             ],
#         )

#     def _step2(self, word):
#         """Implements Step 2 from "An algorithm for suffix stripping"

#         From the paper:

#         Step 2

#             (m>0) ATIONAL ->  ATE       relational     ->  relate
#             (m>0) TIONAL  ->  TION      conditional    ->  condition
#                                         rational       ->  rational
#             (m>0) ENCI    ->  ENCE      valenci        ->  valence
#             (m>0) ANCI    ->  ANCE      hesitanci      ->  hesitance
#             (m>0) IZER    ->  IZE       digitizer      ->  digitize
#             (m>0) ABLI    ->  ABLE      conformabli    ->  conformable
#             (m>0) ALLI    ->  AL        radicalli      ->  radical
#             (m>0) ENTLI   ->  ENT       differentli    ->  different
#             (m>0) ELI     ->  E         vileli        - >  vile
#             (m>0) OUSLI   ->  OUS       analogousli    ->  analogous
#             (m>0) IZATION ->  IZE       vietnamization ->  vietnamize
#             (m>0) ATION   ->  ATE       predication    ->  predicate
#             (m>0) ATOR    ->  ATE       operator       ->  operate
#             (m>0) ALISM   ->  AL        feudalism      ->  feudal
#             (m>0) IVENESS ->  IVE       decisiveness   ->  decisive
#             (m>0) FULNESS ->  FUL       hopefulness    ->  hopeful
#             (m>0) OUSNESS ->  OUS       callousness    ->  callous
#             (m>0) ALITI   ->  AL        formaliti      ->  formal
#             (m>0) IVITI   ->  IVE       sensitiviti    ->  sensitive
#             (m>0) BILITI  ->  BLE       sensibiliti    ->  sensible
#         """

#         if self.mode == self.NLTK_EXTENSIONS:
#             # Instead of applying the ALLI -> AL rule after '(a)bli' per
#             # the published algorithm, instead we apply it first, and,
#             # if it succeeds, run the result through step2 again.
#             if word.endswith("alli") and self._has_positive_measure(
#                 self._replace_suffix(word, "alli", "")
#             ):
#                 return self._step2(self._replace_suffix(word, "alli", "al"))

#         bli_rule = ("bli", "ble", self._has_positive_measure)
#         abli_rule = ("abli", "able", self._has_positive_measure)

#         rules = [
#             ("ational", "ate", self._has_positive_measure),
#             ("tional", "tion", self._has_positive_measure),
#             ("enci", "ence", self._has_positive_measure),
#             ("anci", "ance", self._has_positive_measure),
#             ("izer", "ize", self._has_positive_measure),
#             abli_rule if self.mode == self.ORIGINAL_ALGORITHM else bli_rule,
#             ("alli", "al", self._has_positive_measure),
#             ("entli", "ent", self._has_positive_measure),
#             ("eli", "e", self._has_positive_measure),
#             ("ousli", "ous", self._has_positive_measure),
#             ("ization", "ize", self._has_positive_measure),
#             ("ation", "ate", self._has_positive_measure),
#             ("ator", "ate", self._has_positive_measure),
#             ("alism", "al", self._has_positive_measure),
#             ("iveness", "ive", self._has_positive_measure),
#             ("fulness", "ful", self._has_positive_measure),
#             ("ousness", "ous", self._has_positive_measure),
#             ("aliti", "al", self._has_positive_measure),
#             ("iviti", "ive", self._has_positive_measure),
#             ("biliti", "ble", self._has_positive_measure),
#         ]

#         if self.mode == self.NLTK_EXTENSIONS:
#             rules.append(("fulli", "ful", self._has_positive_measure))

#             # The 'l' of the 'logi' -> 'log' rule is put with the stem,
#             # so that short stems like 'geo' 'theo' etc work like
#             # 'archaeo' 'philo' etc.
#             rules.append(
#                 ("logi", "log", lambda stem: self._has_positive_measure(word[:-3]))
#             )

#         if self.mode == self.MARTIN_EXTENSIONS:
#             rules.append(("logi", "log", self._has_positive_measure))

#         return self._apply_rule_list(word, rules)

#     def _step3(self, word):
#         """Implements Step 3 from "An algorithm for suffix stripping"

#         From the paper:

#         Step 3

#             (m>0) ICATE ->  IC              triplicate     ->  triplic
#             (m>0) ATIVE ->                  formative      ->  form
#             (m>0) ALIZE ->  AL              formalize      ->  formal
#             (m>0) ICITI ->  IC              electriciti    ->  electric
#             (m>0) ICAL  ->  IC              electrical     ->  electric
#             (m>0) FUL   ->                  hopeful        ->  hope
#             (m>0) NESS  ->                  goodness       ->  good
#         """
#         return self._apply_rule_list(
#             word,
#             [
#                 ("icate", "ic", self._has_positive_measure),
#                 ("ative", "", self._has_positive_measure),
#                 ("alize", "al", self._has_positive_measure),
#                 ("iciti", "ic", self._has_positive_measure),
#                 ("ical", "ic", self._has_positive_measure),
#                 ("ful", "", self._has_positive_measure),
#                 ("ness", "", self._has_positive_measure),
#             ],
#         )

#     def _step4(self, word):
#         """Implements Step 4 from "An algorithm for suffix stripping"

#         Step 4

#             (m>1) AL    ->                  revival        ->  reviv
#             (m>1) ANCE  ->                  allowance      ->  allow
#             (m>1) ENCE  ->                  inference      ->  infer
#             (m>1) ER    ->                  airliner       ->  airlin
#             (m>1) IC    ->                  gyroscopic     ->  gyroscop
#             (m>1) ABLE  ->                  adjustable     ->  adjust
#             (m>1) IBLE  ->                  defensible     ->  defens
#             (m>1) ANT   ->                  irritant       ->  irrit
#             (m>1) EMENT ->                  replacement    ->  replac
#             (m>1) MENT  ->                  adjustment     ->  adjust
#             (m>1) ENT   ->                  dependent      ->  depend
#             (m>1 and (*S or *T)) ION ->     adoption       ->  adopt
#             (m>1) OU    ->                  homologou      ->  homolog
#             (m>1) ISM   ->                  communism      ->  commun
#             (m>1) ATE   ->                  activate       ->  activ
#             (m>1) ITI   ->                  angulariti     ->  angular
#             (m>1) OUS   ->                  homologous     ->  homolog
#             (m>1) IVE   ->                  effective      ->  effect
#             (m>1) IZE   ->                  bowdlerize     ->  bowdler

#         The suffixes are now removed. All that remains is a little
#         tidying up.
#         """
#         measure_gt_1 = lambda stem: self._measure(stem) > 1

#         return self._apply_rule_list(
#             word,
#             [
#                 ("al", "", measure_gt_1),
#                 ("ance", "", measure_gt_1),
#                 ("ence", "", measure_gt_1),
#                 ("er", "", measure_gt_1),
#                 ("ic", "", measure_gt_1),
#                 ("able", "", measure_gt_1),
#                 ("ible", "", measure_gt_1),
#                 ("ant", "", measure_gt_1),
#                 ("ement", "", measure_gt_1),
#                 ("ment", "", measure_gt_1),
#                 ("ent", "", measure_gt_1),
#                 # (m>1 and (*S or *T)) ION ->
#                 (
#                     "ion",
#                     "",
#                     lambda stem: self._measure(stem) > 1 and stem[-1] in ("s", "t"),
#                 ),
#                 ("ou", "", measure_gt_1),
#                 ("ism", "", measure_gt_1),
#                 ("ate", "", measure_gt_1),
#                 ("iti", "", measure_gt_1),
#                 ("ous", "", measure_gt_1),
#                 ("ive", "", measure_gt_1),
#                 ("ize", "", measure_gt_1),
#             ],
#         )

#     def _step5a(self, word):
#         """Implements Step 5a from "An algorithm for suffix stripping"

#         From the paper:

#         Step 5a

#             (m>1) E     ->                  probate        ->  probat
#                                             rate           ->  rate
#             (m=1 and not *o) E ->           cease          ->  ceas
#         """
#         # Note that Martin's test vocabulary and reference
#         # implementations are inconsistent in how they handle the case
#         # where two rules both refer to a suffix that matches the word
#         # to be stemmed, but only the condition of the second one is
#         # true.
#         # Earlier in step2b we had the rules:
#         #     (m>0) EED -> EE
#         #     (*v*) ED  ->
#         # but the examples in the paper included "feed"->"feed", even
#         # though (*v*) is true for "fe" and therefore the second rule
#         # alone would map "feed"->"fe".
#         # However, in THIS case, we need to handle the consecutive rules
#         # differently and try both conditions (obviously; the second
#         # rule here would be redundant otherwise). Martin's paper makes
#         # no explicit mention of the inconsistency; you have to infer it
#         # from the examples.
#         # For this reason, we can't use _apply_rule_list here.
#         if word.endswith("e"):
#             stem = self._replace_suffix(word, "e", "")
#             if self._measure(stem) > 1:
#                 return stem
#             if self._measure(stem) == 1 and not self._ends_cvc(stem):
#                 return stem
#         return word

#     def _step5b(self, word):
#         """Implements Step 5a from "An algorithm for suffix stripping"

#         From the paper:

#         Step 5b

#             (m > 1 and *d and *L) -> single letter
#                                     controll       ->  control
#                                     roll           ->  roll
#         """
#         return self._apply_rule_list(
#             word, [("ll", "l", lambda stem: self._measure(word[:-1]) > 1)]
#         )


# [docs]

#     def stem(self, word, to_lowercase=True):
#         """
#         :param to_lowercase: if `to_lowercase=True` the word always lowercase
#         """
#         stem = word.lower() if to_lowercase else word

#         if self.mode == self.NLTK_EXTENSIONS and word in self.pool:
#             return self.pool[stem]

#         if self.mode != self.ORIGINAL_ALGORITHM and len(word) <= 2:
#             # With this line, strings of length 1 or 2 don't go through
#             # the stemming process, although no mention is made of this
#             # in the published algorithm.
#             return stem

#         stem = self._step1a(stem)
#         stem = self._step1b(stem)
#         stem = self._step1c(stem)
#         stem = self._step2(stem)
#         stem = self._step3(stem)
#         stem = self._step4(stem)
#         stem = self._step5a(stem)
#         stem = self._step5b(stem)

#         return stem


#     def __repr__(self):
#         return "<PorterVanillaPyStemmer>"

# '''


# Define what gets exported when someone does "from porter_stemmer import *"
__all__ = [
    "PorterVanillaPyStemmer",
    # 'stem_file_wrapper',
    "run_comprehensive_tests",
]


class PorterVanillaPyStemmer:
    """
    A production-ready implementation of the Porter Stemming Algorithm.

    This class implements the Porter Stemmer with Martin Porter's recommended
    extensions. It provides methods for stemming individual words or entire
    documents while preserving formatting and punctuation.

    Attributes:
        to_lowercase (bool): Whether to convert words
          to lowercase before stemming
        preserve_original_on_error (bool): Whether to return
          original word on errors

    Example:
        >>> stemmer = PorterVanillaPyStemmer()
        >>> stemmer.stem_word("running")
        'run'
        >>> stemmer.stem_document("The boys are running quickly!")
        'The boy are run quickli!'
    """

    def __init__(
        self,
        to_lowercase: bool = True,
        preserve_original_on_error: bool = True,
        mode: str = "ORIGINAL",
    ):
        """
        Initialize the Porter Stemmer.

        Args:
            to_lowercase (bool): If True, convert words to
              lowercase before stemming.
                                Default is True.
            preserve_original_on_error (bool): If True, return
              original word when
                                            errors occur. Default is True.
            mode (str): Either "ORIGINAL" for standard Porter algorithm or
                    "NLTK_EXTENSIONS" to include NLTK's modifications.
                    Default is "ORIGINAL".
        """
        # Configuration options
        self.to_lowercase = to_lowercase
        self.preserve_original_on_error = preserve_original_on_error
        self.mode = mode

        # Define vowels for the algorithm
        self.vowels = set("aeiouAEIOU")

        # Compile regex patterns for document processing
        # This pattern matches words (sequences of alphabetic characters)
        # self.word_pattern = re.compile(r'\b[a-zA-Z]+\b')

        # For production use, support Unicode: matches only Unicode letters
        self.word_pattern = re.compile(r"\b[^\W\d_]+\b", re.UNICODE)

        # Define special words for ORIGINAL mode
        # These are only words that fundamentally break the algorithm
        self.original_special_words = {
            "sky": "sky",  # Doesn't follow normal rules
            "skies": "sky",  # Irregular plural
            "news": "news",  # Always singular
            "innings": "inning",  # Sports term
            "outing": "outing",  # Would become 'out' otherwise
            "canning": "canning",  # Preserves meaning
            "howe": "howe",  # Proper noun
            "proceed": "proceed",  # Preserve meaning
            "exceed": "exceed",  # Preserve meaning
            "succeed": "succeed",  # Preserve meaning
        }

        # Define all special words (including NLTK extensions)
        # Used when mode == "NLTK_EXTENSIONS"
        self.special_words = {
            "sky": "sky",
            "skies": "sky",
            "dies": "die",  # NLTK-style extension: prevent 'dies' -> 'di'
            "ties": "tie",  # NLTK-style extension: prevent 'ties' -> 'ti'
            "lies": "lie",  # NLTK-style extension: prevent 'lies' -> 'li'
            "dying": "die",
            "lying": "lie",
            "tying": "tie",
            "news": "news",
            "innings": "inning",
            "outing": "outing",
            "canning": "canning",
            "howe": "howe",
            "proceed": "proceed",
            "exceed": "exceed",
            "succeed": "succeed",
        }

    def stem_word(self, word: str) -> str:
        """
        Stem a single word using the Porter algorithm.

        Args:
            word (str): The word to stem.
            Should contain only alphabetic characters.

        Returns:
            str: The stemmed word.

        Raises:
            TypeError: If word is not a string.
            ValueError: If word is None or empty.

        Example:
            >>> stemmer = PorterVanillaPyStemmer()
            >>> stemmer.stem_word("running")
            'run'
        """
        # Input validation
        if word is None:
            raise ValueError("Word cannot be None")
        if not isinstance(word, str):
            raise TypeError(f"Word must be a string, got {type(word).__name__}")
        if not word:
            raise ValueError("Word cannot be empty")

        # Store original word for error handling and case preservation
        original_word = word

        try:
            # Handle special cases based on mode
            word_lower = word.lower()

            # Check special words based on mode
            if self.mode == "NLTK_EXTENSIONS":
                # In NLTK mode, use all special words
                if word_lower in self.special_words:
                    result = self.special_words[word_lower]
                    # Preserve case if needed
                    if not self.to_lowercase:
                        result = self._apply_case_pattern(original_word, result)
                    return result
            else:
                # In ORIGINAL mode, only use limited special words
                if word_lower in self.original_special_words:
                    result = self.original_special_words[word_lower]
                    # Preserve case if needed
                    if not self.to_lowercase:
                        result = self._apply_case_pattern(original_word, result)
                    return result

            # Apply lowercase for processing
            word = word_lower

            # Skip very short words (length 1 or 2)
            if len(word) <= 2:
                # Apply case pattern if not lowercasing
                if not self.to_lowercase:
                    return self._apply_case_pattern(original_word, word)
                return word

            # Apply Porter algorithm steps in sequence
            word = self._step1a(word)
            word = self._step1b(word)
            word = self._step1c(word)
            word = self._step2(word)
            word = self._step3(word)
            word = self._step4(word)
            word = self._step5a(word)
            word = self._step5b(word)

            # Apply case pattern if needed
            if not self.to_lowercase:
                word = self._apply_case_pattern(original_word, word)

            return word

        except Exception as e:
            # Handle any unexpected errors gracefully
            if self.preserve_original_on_error:
                return original_word
            else:
                raise RuntimeError(
                    f"Error stemming word '{original_word}': {str(e)}"
                ) from e

    # # alternative 1:
    # def _clean_non_alphanumeric_characters_and_normalize_spaces_with_apostrophe_handling(
    #     self,
    #     text: str,
    #     preserve_contractions: bool = True
    # ) -> str:
    #     """
    #     Replace non-alphanumeric characters with spaces and normalize spacing,
    #     with intelligent apostrophe handling for contractions.

    #     This method provides more sophisticated text cleaning that can handle
    #     contractions (don't, can't, I'm) more intelligently than simply
    #     removing all punctuation.

    #     Args:
    #         text (str): The input text to clean.
    #         preserve_contractions (bool): If True, attempts to handle common
    #                                     contractions intelligently. If False,
    #                                     treats apostrophes like other punctuation.
    #                                     Default is True.

    #     Returns:
    #         str: The cleaned text with intelligent apostrophe handling.

    #     Examples:
    #         With preserve_contractions=True:
    #         "don't" -> "do not" or "dont" (depending on implementation)
    #         "I'm happy" -> "I am happy" or "im happy"
    #         "John's car" -> "john s car" (possessive kept separate)

    #         With preserve_contractions=False:
    #         "don't" -> "don t" (same as original method)
    #     """
    #     if preserve_contractions:
    #         # Define common contraction expansions
    #         # This is a basic set - you could expand this significantly
    #         contraction_expansions = {
    #             # Common contractions
    #             "don't": "do not",
    #             "won't": "will not",
    #             "can't": "cannot",
    #             "shouldn't": "should not",
    #             "wouldn't": "would not",
    #             "couldn't": "could not",
    #             "isn't": "is not",
    #             "aren't": "are not",
    #             "wasn't": "was not",
    #             "weren't": "were not",
    #             "haven't": "have not",
    #             "hasn't": "has not",
    #             "hadn't": "had not",

    #             # I contractions
    #             "i'm": "i am",
    #             "i've": "i have",
    #             "i'll": "i will",
    #             "i'd": "i would",

    #             # You contractions
    #             "you're": "you are",
    #             "you've": "you have",
    #             "you'll": "you will",
    #             "you'd": "you would",

    #             # Other common ones
    #             "we're": "we are",
    #             "we've": "we have",
    #             "we'll": "we will",
    #             "we'd": "we would",
    #             "they're": "they are",
    #             "they've": "they have",
    #             "they'll": "they will",
    #             "they'd": "they would",
    #             "there's": "there is",
    #             "here's": "here is",
    #             "what's": "what is",
    #             "that's": "that is",
    #             "it's": "it is",
    #             "he's": "he is",
    #             "she's": "she is",

    #             # Less common but important
    #             "let's": "let us",
    #             "who's": "who is",
    #             "where's": "where is",
    #             "how's": "how is",
    #             "when's": "when is",
    #         }

    #         # Convert to lowercase for matching (we'll preserve case later if needed)
    #         text_lower = text.lower()

    #         # Replace contractions with expansions
    #         for contraction, expansion in contraction_expansions.items():
    #             # Use word boundaries to avoid partial matches
    #             pattern = r'\b' + re.escape(contraction) + r'\b'
    #             text_lower = re.sub(pattern, expansion, text_lower)

    #         # Now remove remaining non-alphanumeric characters
    #         # This will handle possessives (john's -> john s) and other apostrophes
    #         cleaned_text = re.sub(r'[^a-zA-Z0-9]+', ' ', text_lower)

    #     else:
    #         # Original behavior - treat apostrophes like any other punctuation
    #         cleaned_text = re.sub(r'[^a-zA-Z0-9]+', ' ', text)

    #     # Normalize spaces and trim
    #     return cleaned_text.strip()

    # # # alternative 2
    # def _clean_non_alphanumeric_characters_and_normalize_spaces(
    #     self,
    #     text: str
    # ) -> str:
    #     """
    #     Clean text while preserving apostrophes within words (contractions/possessives).

    #     This approach keeps apostrophes that appear between letters but removes
    #     other punctuation. This preserves contractions like "don't" and possessives
    #     like "John's" while still removing other punctuation.

    #     Examples:
    #         "don't go!" -> "don't go"
    #         "John's car" -> "John's car"
    #         "test@email.com" -> "test email com"
    #         "it's a 'test'" -> "it's a test"
    #     """
    #     # First pass: Replace non-alphanumeric characters EXCEPT apostrophes with spaces
    #     # But be careful about apostrophes - only keep them between letters

    #     # This regex preserves apostrophes that are between word characters
    #     # but removes apostrophes at start/end of sequences
    #     result = ""
    #     i = 0
    #     while i < len(text):
    #         char = text[i]
    #         if char.isalnum():
    #             # Keep alphanumeric characters
    #             result += char
    #         elif char == "'" and i > 0 and i < len(text) - 1:
    #             # Keep apostrophe only if it's between word characters
    #             if text[i-1].isalpha() and text[i + 1].isalpha():
    #                 result += char
    #             else:
    #                 result += " "
    #         else:
    #             # Replace all other characters with space
    #             result += " "
    #         i += 1

    #     # Normalize multiple spaces
    #     result = re.sub(r'\s+', ' ', result)
    #     return result.strip()

    # # # simplest, no exceptions
    # def _clean_non_alphanumeric_characters_and_normalize_spaces(self, text: str) -> str:
    #     """
    #     Replace all non-alphanumeric characters with spaces
    #     and normalize multiple spaces.

    #     This method performs two sequential text cleaning operations:
    #     1. Replaces every character that is not a letter (a-z, A-Z) or digit (0-9)
    #         with a single space character. This includes:
    #         - Punctuation marks (.,!?;:"'- etc.)
    #         - Special characters (@#$%^&* etc.)
    #         - Whitespace characters (newlines \n, tabs \t, carriage returns \r)
    #         - Unicode symbols and non-Latin characters

    #     2. Normalizes spacing by replacing any sequence of multiple spaces with
    #         exactly one space, and removes leading/trailing spaces.

    #     This preprocessing step is useful for:
    #     - Substring matching where punctuation differences should be ignored
    #     - Creating searchable text indices
    #     - Normalizing text before NLP processing
    #     - Removing formatting artifacts from documents

    #     Args:
    #         text (str): The input text to clean. Can contain
    #         any Unicode characters.
    #                     Must not be None (validated by caller).

    #     Returns:
    #         str: The cleaned text with only alphanumeric characters and single
    #           spaces.
    #             Empty string returns empty string.

    #     Examples:
    #         >>> cleaner._clean_non_alphanumeric_characters_and_normalize_spaces(
    #         ...     "Hello, world! How are you?")
    #         'Hello world How are you'

    #         >>> cleaner._clean_non_alphanumeric_characters_and_normalize_spaces(
    #         ...     "user@email.com\n\tPhone: (555) 123-4567")
    #         'user email com Phone 555 123 4567'

    #         >>> cleaner._clean_non_alphanumeric_characters_and_normalize_spaces(
    #         ...     "don't   use   multiple     spaces")
    #         'don t use multiple spaces'

    #     Implementation Notes:
    #         - Uses regex for efficiency with large texts
    #         - The pattern [^a-zA-Z0-9]+ matches one or more
    #           non-alphanumeric characters
    #         - The + quantifier groups consecutive non-alphanumeric
    #           characters for efficiency
    #         - strip() removes leading/trailing spaces after replacement
    #         - This method assumes text is already a valid string
    #           (caller validates)
    #     """
    #     # Replace all non-alphanumeric characters with a single space
    #     # The regex pattern [^a-zA-Z0-9]+ means:
    #     # [^...] - NOT any of these characters
    #     # a-zA-Z - lowercase and uppercase letters
    #     # 0-9 - digits
    #     # + - one or more occurrences (groups consecutive non-alphanumeric chars)
    #     text_with_only_alphanumeric_and_spaces = re.sub(r"[^a-zA-Z0-9]+", " ", text)

    #     # Remove leading/trailing spaces and return
    #     # strip() handles cases where non-alphanumeric chars were at start/end
    #     cleaned_and_trimmed_text = text_with_only_alphanumeric_and_spaces.strip()

    #     return cleaned_and_trimmed_text

    def _clean_non_alphanumeric_characters_and_normalize_spaces(self, text: str) -> str:
        """
        Replace specific punctuation and special characters with spaces while preserving
        letters (including Unicode), numbers, and apostrophes.

        This method uses a deny-list approach, specifically removing only known
        punctuation and special characters while preserving:
        - All Unicode letters (including accented characters like é, ñ, etc.)
        - All numbers
        - Apostrophes (for contractions like "don't" and possessives like "Mary's")

        Characters that are replaced with spaces:
        - Whitespace: newlines (\n), tabs (\t), carriage returns (\r)
        - Common punctuation: . , ! ? ; : " ( ) [ ] { } < > / \ | @ # $ % ^ & * + - = _ ~
        - Other special characters: `

        This approach is more inclusive for international text while still removing
        formatting and punctuation that typically interferes with text analysis.

        Args:
            text (str): The input text to clean. Can contain any Unicode characters.
                        Must not be None (validated by caller).

        Returns:
            str: The cleaned text with punctuation replaced by spaces, apostrophes
                preserved, and multiple spaces normalized to single spaces.

        Examples:
            >>> cleaner._clean_non_alphanumeric_characters_and_normalize_spaces(
            ...     "Hello, world! How are you?")
            'Hello world How are you'

            >>> cleaner._clean_non_alphanumeric_characters_and_normalize_spaces(
            ...     "user@email.com\n\tPhone: (555) 123-4567")
            'user email com Phone 555 123 4567'

            >>> cleaner._clean_non_alphanumeric_characters_and_normalize_spaces(
            ...     "don't forget Mary's résumé")
            "don't forget Mary's résumé"

            >>> cleaner._clean_non_alphanumeric_characters_and_normalize_spaces(
            ...     "UTF-8: café résumé naïve")
            'UTF 8 café résumé naïve'

        Implementation Notes:
            - Uses character replacement for efficiency
            - Preserves apostrophes to maintain contractions and possessives
            - Preserves Unicode letters to support international text
            - The deny-list approach is more maintainable than allow-list for Unicode
        """
        # Define characters to replace with spaces
        # Note: We're NOT including apostrophe (') in this list
        characters_to_remove = (
            # Whitespace characters
            "\n\t\r"
            # Common punctuation
            '.,!?;:"()[]{}/<>\\|'
            # Special characters and symbols
            "@#$%^&*+-=_~`"
            # Additional quotation marks
            '""«»'
            # Common symbols
            "§¶†‡•·"
        )

        # Create translation table
        # This maps each character to remove to a space
        translation_table = str.maketrans(
            characters_to_remove, " " * len(characters_to_remove)
        )

        # Apply the translation
        text_with_punctuation_replaced = text.translate(translation_table)

        # Normalize multiple spaces to single space
        # This regex replaces any sequence of whitespace with a single space
        normalized_text = re.sub(r"\s+", " ", text_with_punctuation_replaced)

        # Remove leading/trailing spaces and return
        cleaned_and_trimmed_text = normalized_text.strip()

        return cleaned_and_trimmed_text

    def stem_document(
        self,
        text: str,
        clean_non_alphanumeric: bool = False,
    ) -> str:
        """
        Stem all words in a document
        while preserving formatting and punctuation.

        Args:
            text (str): The document text to process.
            clean_non_alphanumeric (bool): If True,
            replaces all non-alphanumeric
                characters with spaces and normalizes spacing
                BEFORE stemming. This includes removing
                punctuation, special characters, and extra
                whitespace. Default is False.

                When True:
                - "user@email.com" becomes "user email com"
                - "don't" becomes "don t"
                - "hello\n\tworld" becomes "hello world"

                Useful for substring matching and text indexing
                where punctuation should be ignored.

        Returns:
            str: The document with all words stemmed.
            If clean_non_alphanumeric=True,
                the output will contain only alphanumeric characters
                and single spaces.

        Raises:
            TypeError: If text is not a string.
            ValueError: If text is None.

        Example:
            >>> stemmer = PorterVanillaPyStemmer()
            >>> stemmer.stem_document("The boys are running quickly!")
            'The boy are run quickli!'

            >>> stemmer.stem_document("The boys are running quickly!",
            clean_non_alphanumeric=True)
            'the boy are run quickli'

            >>> stemmer.stem_document("user@email.com, phone: (555) 123-4567",
            clean_non_alphanumeric=True)
            'user email com phone 555 123 4567'
        """

        # Input validation
        if text is None:
            raise ValueError("Text cannot be None")
        if not isinstance(text, str):
            raise TypeError(f"Text must be a string, got {type(text).__name__}")

        # Handle empty text
        if not text:
            return text

        # Apply non-alphanumeric cleaning if requested
        # This happens BEFORE stemming to ensure clean input
        if clean_non_alphanumeric:
            text = self._clean_non_alphanumeric_characters_and_normalize_spaces(text)
            # After cleaning, we might have an empty string
            if not text:
                return text

        # Process the document by replacing each word with its stemmed version
        def replace_word(match):
            """Replace a matched word with its stemmed version."""
            word = match.group(0)
            try:
                return self.stem_word(word)
            except Exception:
                # If stemming fails, return original word
                return word

        # Use regex to find and replace all words
        stemmed_text = self.word_pattern.sub(replace_word, text)

        return stemmed_text

    def stem_tokens(self, tokens: List[str]) -> List[str]:
        """
        Stem a list of pre-tokenized words.

        Args:
        tokens (List[str]): List of words to stem.

        Returns:
        List[str]: List of stemmed words in the same order.

        Raises:
        TypeError: If tokens is not a list or contains non-string elements.
        ValueError: If tokens is None.

        Example:
        >>> stemmer = PorterVanillaPyStemmer()
        >>> stemmer.stem_tokens(['running', 'flies', 'happily'])
        ['run', 'fli', 'happili']
        """
        # Input validation
        if tokens is None:
            raise ValueError("Tokens cannot be None")
        if not isinstance(tokens, list):
            raise TypeError(f"Tokens must be a list, got {type(tokens).__name__}")

        # Process each token
        stemmed_tokens = []
        for i, token in enumerate(tokens):
            if not isinstance(token, str):
                raise TypeError(
                    f"Token at index {i} must be a string, got {type(token).__name__}"
                )

            try:
                stemmed_token = self.stem_word(token)
                stemmed_tokens.append(stemmed_token)
            except Exception as e:
                if self.preserve_original_on_error:
                    stemmed_tokens.append(token)
                else:
                    raise RuntimeError(
                        f"Error stemming token at index {i}: {str(e)}"
                    ) from e

        return stemmed_tokens

    def _apply_case_pattern(self, original_word: str, stemmed_word: str) -> str:
        """
        Apply the case pattern from the original word to the stemmed result.

        This method maps the uppercase/lowercase pattern from the original word
        onto the stemmed word. This allows preservation of case patterns like
        'FLIES' -> 'FLI' or 'RuNNinG' -> 'RuN'.

        The method handles several cases:
        1. All uppercase original -> all uppercase result
        2. All lowercase original -> all lowercase result
        3. Mixed case original -> apply pattern character by character
        4. Stemmed word longer than original -> extra characters stay lowercase
        5. Empty strings -> return empty string

        Character Requirements:
        This method enforces that the original word
        must contain ONLY alphabetic
        characters (A-Z, a-z). No punctuation, digits, or
        special characters are
        allowed. This constraint ensures consistent behavior
        with the rest of the
        Porter Stemmer implementation, which is designed for
        pure alphabetic text.

        Words containing apostrophes (like "don't"), hyphens (like
        "pre-process"),
        or any other non-alphabetic characters must be pre-processed
        before being
        passed to this stemmer. The stem_document() method handles this by only
        extracting alphabetic sequences.

        Args:
        original_word (str): The original word with its case pattern.
                Must be a non-None string containing ONLY alphabetic
                characters. Can be empty. The case pattern from this
                word will be applied to the stemmed version.
                Example: 'RuNNinG', 'FLIES', 'happy'

        stemmed_word (str): The stemmed word (usually lowercase).
                            Must be a non-None string. Can be empty. This is
                            typically the output from the stemming algorithm.
                            Example: 'run', 'fli', 'happi'

        Returns:
        str: The stemmed word with the original case pattern applied.
                If stemmed_word is empty, returns empty string.
                If original_word is empty, returns stemmed_word in lowercase.
                If original is all caps, returns stemmed in all caps.
                If original is mixed case, applies pattern position by position.

        Raises:
        TypeError: If either argument is not a string or is None.
                    Specific error message indicates which argument is invalid.
        ValueError: If original_word contains any non-alphabetic characters.
                    Error message lists the specific invalid characters found.
        RuntimeError: If an unexpected error occurs during character processing.
                    Includes position information for debugging.

        Examples:
        >>> stemmer = PorterVanillaPyStemmer(to_lowercase=False)
        >>> stemmer._apply_case_pattern('FLIES', 'fli')
        'FLI'
        >>> stemmer._apply_case_pattern('Running', 'run')
        'Run'
        >>> stemmer._apply_case_pattern('HaPpY', 'happi')
        'HaPpI'
        >>> stemmer._apply_case_pattern('ABC', 'abcdef')
        'ABCdef'
        >>> stemmer._apply_case_pattern('', 'test')
        'test'
        >>> stemmer._apply_case_pattern('Test', '')
        ''

        # These would raise ValueError:
        >>> stemmer._apply_case_pattern("don't", 'do')  # Contains apostrophe
        ValueError: original_word contains non-alphabetic characters: ["'"]...
        >>> stemmer._apply_case_pattern('pre-process', 'preprocess')  # Contains hyphen
        ValueError: original_word contains non-alphabetic characters: ['-']...

        Implementation Notes:
        - This is a private method called by stem_word() when to_lowercase=False
        - Assumes stemmed_word is already valid output from the stemming algorithm
        - Does not modify the actual stem, only its case presentation
        - Uses character-by-character processing for mixed case patterns
        - Optimizes for common cases (all upper, all lower) for performance
        - Extra characters in stemmed word (beyond original length) default to lowercase

        Algorithm:
        1. Validate inputs (non-None, string type, alphabetic only)
        2. Handle edge cases (empty strings)
        3. Check for optimization opportunities (all upper/lower)
        4. For mixed case: iterate through stemmed word positions
        - If position exists in original, copy its case
        - If position beyond original length, use lowercase
        5. Return the case-adjusted result
        """
        # Comprehensive input validation
        if original_word is None:
            raise TypeError("original_word cannot be None")
        if stemmed_word is None:
            raise TypeError("stemmed_word cannot be None")

        # Type checking for both arguments
        if not isinstance(original_word, str):
            raise TypeError(
                f"original_word must be a string, got {type(original_word).__name__}"
            )
        if not isinstance(stemmed_word, str):
            raise TypeError(
                f"stemmed_word must be a string, got {type(stemmed_word).__name__}"
            )

        # Handle empty stemmed word - nothing to apply pattern to
        if not stemmed_word:
            return stemmed_word

        # Handle empty original word - return stemmed word as lowercase
        if not original_word:
            return stemmed_word.lower()

        # Validate that original word contains only alphabetic characters
        # The Porter Stemmer is designed for pure alphabetic input
        if not original_word.isalpha():
            non_alpha_chars = [char for char in original_word if not char.isalpha()]
            raise ValueError(
                f"original_word contains non-alphabetic characters: {non_alpha_chars}. "
                f"The Porter Stemmer only processes alphabetic characters. "
                f"Pre-process your text to handle punctuation, contractions, and hyphenated words."
            )

        # Check if original is all uppercase - common case optimization
        if original_word.isupper():
            return stemmed_word.upper()

        # Check if original is all lowercase - common case optimization
        if original_word.islower():
            return stemmed_word.lower()

        # Handle mixed case - apply pattern character by character
        # Build result character list for efficiency (avoid string concatenation)
        result_characters = []

        # Process each character in the stemmed word
        for char_position, stemmed_char in enumerate(stemmed_word):
            try:
                # Check if we have a corresponding character in the original word
                if char_position < len(original_word):
                    original_char_at_position = original_word[char_position]

                    # Apply the case from the corresponding position
                    if original_char_at_position.isupper():
                        result_characters.append(stemmed_char.upper())
                    else:
                        result_characters.append(stemmed_char.lower())
                else:
                    # Stemmed word is longer than original
                    # Keep remaining characters lowercase by default
                    # This handles cases where stemming produces a longer result
                    result_characters.append(stemmed_char.lower())

            except Exception as char_processing_error:
                # Catch any unexpected errors during character processing
                # Include position information for debugging
                raise RuntimeError(
                    f"Error processing character at position {char_position} "
                    f"(original: '{original_word}', stemmed: '{stemmed_word}'): "
                    f"{str(char_processing_error)}"
                ) from char_processing_error

        # Join the result characters into final string
        final_result = "".join(result_characters)

        return final_result

    def _is_consonant(self, word: str, index: int) -> bool:
        """
        Check if the character at the given index is a consonant.

        In Porter's algorithm, a consonant is defined as:
        - Any letter that is not a, e, i, o, or u
        - The letter 'y' is a consonant if:
                - It's at the beginning of the word, OR
                - It's preceded by a vowel
        - The letter 'y' is a vowel if preceded by a consonant

        This definition means 'y' can be either vowel or consonant depending
        on context, which affects the stemming rules.

        Args:
        word (str): The word being analyzed. Must be a non-empty string
                    containing only alphabetic characters (already lowercase).
                    Example: 'happy', 'syzygy', 'yellow'

        index (int): The index of the character to check. Must be a valid
                    index within the word (0 <= index < len(word)).
                    Example: 0, 1, 2, etc.

        Returns:
        bool: True if the character at word[index] is a consonant according
                to Porter's definition, False if it's a vowel.

                Examples:
                    - 'happy'[0] ('h') -> True (consonant)
                    - 'happy'[1] ('a') -> False (vowel)
                    - 'happy'[4] ('y') -> True (consonant after consonant 'p')
                    - 'yellow'[0] ('y') -> True (consonant at start)
                    - 'boyish'[2] ('y') -> False (vowel after vowel 'o')

        Raises:
        TypeError: If word is not a string or index is not an integer
        ValueError: If word is None or empty
        IndexError: If index is out of bounds for the given word
        ValueError: If word contains non-alphabetic characters

        Examples:
        >>> stemmer._is_consonant('happy', 0)  # 'h'
        True
        >>> stemmer._is_consonant('happy', 1)  # 'a'
        False
        >>> stemmer._is_consonant('yellow', 0)  # 'y' at start
        True
        >>> stemmer._is_consonant('boyish', 2)  # 'y' after vowel
        False

        Implementation Notes:
        - This is a core method used by _measure() and other stemming steps
        - Assumes word is already lowercase (handled by stem_word())
        - The special 'y' handling is crucial for correct stemming
        """
        # Input validation - check word parameter
        if word is None:
            raise ValueError("word cannot be None")

        if not isinstance(word, str):
            raise TypeError(f"word must be a string, got {type(word).__name__}")

        if not word:
            raise ValueError("word cannot be empty")

        # Validate index parameter
        if not isinstance(index, int):
            raise TypeError(f"index must be an integer, got {type(index).__name__}")

        # Boundary checking for index
        if index < 0:
            raise IndexError(f"index {index} is negative. Must be >= 0")

        if index >= len(word):
            raise IndexError(
                f"index {index} is out of range for word of length {len(word)}"
            )

        # Validate word contains only alphabetic characters
        if not word.isalpha():
            invalid_chars = [char for char in word if not char.isalpha()]
            raise ValueError(
                f"word contains non-alphabetic characters: {invalid_chars}"
            )

        try:
            # Get the character at the specified index
            character_to_check = word[index]

            # Check if it's a standard vowel (a, e, i, o, u)
            # Using set membership for efficiency
            if character_to_check in self.vowels:
                return False  # It's a vowel, not a consonant

            # Special handling for 'y' - the tricky case
            if character_to_check.lower() == "y":
                # 'y' at the start of a word is always a consonant
                # Examples: 'yellow', 'yes', 'yodel'
                if index == 0:
                    return True

                # For 'y' not at the start, check the previous character
                # If previous character is a vowel, 'y' is a consonant
                # If previous character is a consonant, 'y' is a vowel
                try:
                    # Recursive call to check the previous character
                    # Safe because we know index > 0 here
                    previous_is_consonant = self._is_consonant(word, index - 1)

                    # If previous is consonant, 'y' is vowel (return False)
                    # If previous is vowel, 'y' is consonant (return True)
                    return not previous_is_consonant

                except Exception as recursion_error:
                    # Handle any errors in recursive call
                    raise RuntimeError(
                        f"Error checking previous character for 'y' at index {index}: "
                        f"{str(recursion_error)}"
                    ) from recursion_error

            # All other letters are consonants
            # This includes all letters except a, e, i, o, u, and special-case y
            return True

        except Exception as unexpected_error:
            # Catch any unexpected errors not already handled
            raise RuntimeError(
                f"Unexpected error checking character at index {index} in word '{word}': "
                f"{str(unexpected_error)}"
            ) from unexpected_error

    def _measure(self, word: str) -> int:
        """
        Calculate the measure (m) of a word according to Porter's algorithm.

        The measure counts the number of vowel-consonant sequences (VC) in a word.
        This is a key concept in the Porter algorithm that determines which
        suffix removal rules can be applied.

        From Porter's paper:
        A consonant will be denoted by c, a vowel by v. A list ccc... of
        length greater than 0 will be denoted by C, and a list vvv... of
        length greater than 0 will be denoted by V. Any word, or part of a
        word, therefore has one of the four forms:
                CVCV ... C
                CVCV ... V
                VCVC ... C
                VCVC ... V
        These may all be represented by the single form [C]VCVC ... [V]
        where the square brackets denote arbitrary presence of their contents.
        Using (VC){m} to denote VC repeated m times, this may again be written
        as [C](VC){m}[V]. m will be called the measure of any word or word
        part when represented in this form.

        Examples from the paper:
        m=0: TR, EE, TREE, Y, BY
        m=1: TROUBLE, OATS, TREES, IVY
        m=2: TROUBLES, PRIVATE, OATEN, ORRERY

        Args:
        word (str): The word to measure. Must be a non-empty string containing
                    only lowercase alphabetic characters. This is typically a
                    word or word stem being evaluated for rule application.
                    Examples: 'tree', 'trouble', 'private'

        Returns:
        int: The measure of the word (number of VC sequences). Will be >= 0.
                Returns 0 for empty words or words with no VC sequences.

                Examples:
                    'tree' -> 0 (pattern: CCV)
                    'trouble' -> 1 (pattern: CCVCCCV with one VC)
                    'private' -> 2 (pattern: CCVCVCV with two VCs)

        Raises:
        TypeError: If word is not a string
        ValueError: If word is None
        ValueError: If word contains non-alphabetic characters
        RuntimeError: If an unexpected error occurs during processing

        Examples:
        >>> stemmer._measure('tree')
        0
        >>> stemmer._measure('trouble')
        1
        >>> stemmer._measure('private')
        2
        >>> stemmer._measure('')
        0

        Implementation Notes:
        - This is a core method used by most stemming rules to check conditions
        - The measure determines if rules like "(m>0) ATIONAL -> ATE" apply
        - Uses _is_consonant() to build the consonant/vowel pattern
        - Empty word returns 0 (no VC sequences)
        """
        # Input validation
        if word is None:
            raise ValueError("word cannot be None")

        if not isinstance(word, str):
            raise TypeError(f"word must be a string, got {type(word).__name__}")

        # Empty word has measure 0 - no vowel-consonant sequences
        if not word:
            return 0

        # Validate word contains only alphabetic characters
        if not word.isalpha():
            invalid_chars = [char for char in word if not char.isalpha()]
            raise ValueError(
                f"word contains non-alphabetic characters: {invalid_chars}. "
                f"Word must contain only alphabetic characters."
            )

        try:
            # Build a pattern string representing consonants ('c') and vowels ('v')
            # This makes it easy to count VC sequences
            consonant_vowel_pattern = ""

            # Analyze each character in the word
            for char_index in range(len(word)):
                try:
                    # Check if character is consonant or vowel
                    if self._is_consonant(word, char_index):
                        consonant_vowel_pattern += "c"
                    else:
                        consonant_vowel_pattern += "v"

                except Exception as char_error:
                    # Handle errors from _is_consonant
                    raise RuntimeError(
                        f"Error analyzing character at position {char_index}: "
                        f"{str(char_error)}"
                    ) from char_error

            # Count the number of 'vc' sequences in the pattern
            # This is the measure value
            vc_sequence_count = 0

            # Look for each occurrence of 'vc' in the pattern
            # We check each adjacent pair of characters
            for pattern_index in range(len(consonant_vowel_pattern) - 1):
                current_char = consonant_vowel_pattern[pattern_index]
                next_char = consonant_vowel_pattern[pattern_index + 1]

                # Check if we have a vowel followed by consonant
                if current_char == "v" and next_char == "c":
                    vc_sequence_count += 1

            # Return the final measure count
            return vc_sequence_count

        except Exception as unexpected_error:
            # Catch any unexpected errors not already handled
            raise RuntimeError(
                f"Unexpected error calculating measure for word '{word}': "
                f"{str(unexpected_error)}"
            ) from unexpected_error

    def _contains_vowel(self, word: str) -> bool:
        """
        Check if the word contains at least one vowel.

        Args:
        word (str): The word to check.

        Returns:
        bool: True if the word contains a vowel, False otherwise.
        """
        for i in range(len(word)):
            if not self._is_consonant(word, i):
                return True
        return False

    def _ends_with_double_consonant(self, word: str) -> bool:
        """
        Check if the word ends with a double consonant (e.g., 'tt', 'ss').

        Args:
        word (str): The word to check.

        Returns:
        bool: True if the word ends with a double consonant.
        """
        # Need at least 2 characters
        if len(word) < 2:
            return False

        # Check if last two characters are the same and both consonants
        return word[-1] == word[-2] and self._is_consonant(word, len(word) - 1)

    def _ends_cvc(self, word: str) -> bool:
        """
        Check if the word ends with consonant-vowel-consonant pattern.

        The final consonant must not be 'w', 'x', or 'y'.
        This is used to determine if an 'e' should be added.

        Args:
        word (str): The word to check.

        Returns:
        bool: True if the word ends with CVC (with restrictions).
        """
        # Need at least 3 characters
        if len(word) < 3:
            return False

        # Check the pattern
        if (
            self._is_consonant(word, len(word) - 3)
            and not self._is_consonant(word, len(word) - 2)
            and self._is_consonant(word, len(word) - 1)
        ):

            # Final consonant must not be w, x, or y
            last_char = word[-1].lower()
            return last_char not in ("w", "x", "y")

        return False

    # original vs. NLTK mode
    # the rule should be: IES → I (unconditionally)
    def _step1a(self, word: str) -> str:
        """
        Apply Step 1a of the Porter algorithm: Remove plural suffixes.

        This method implements the first step of the Porter Stemming Algorithm,
        which deals with removing plural forms. The method processes words ending
        in 's' and applies specific transformation rules based on the exact suffix.

        Standard Porter Algorithm Rules (Porter, 1980):
        1. SSES -> SS  : Words ending in 'sses' have 'es' removed
                            Examples: caresses -> caress, witnesses -> witness

        2. IES -> I    : Words ending in 'ies' have 'es' removed
                            Examples: ponies -> poni, flies -> fli, cries -> cri
                            Note: This produces stems like 'di' from 'dies'

        3. SS -> SS    : Words ending in 'ss' remain unchanged
                            Examples: caress -> caress, princess -> princess

        4. S ->        : Words ending in single 's' have it removed
                            Examples: cats -> cat, runs -> run, helps -> help

        NLTK Extension (when mode == "NLTK_EXTENSIONS"):
        The Natural Language Toolkit (NLTK) project introduced a modification
        to handle certain 4-letter words more intuitively:

        - 4-letter words ending in 'ies' change to 'ie' instead of 'i'
        Examples: dies -> die (not di), ties -> tie (not ti)

        This extension only affects 4-letter words and was added because
        the standard algorithm produces counterintuitive results for common
        short words. When not in NLTK mode, these words follow the standard
        IES -> I rule.

        Processing Order:
        The rules are checked in order of specificity (longest suffix first):
        1. First check for 'sses' (4 characters)
        2. Then check for 'ies' (3 characters, with possible NLTK override)
        3. Then check for 'ss' (2 characters)
        4. Finally check for 's' (1 character)

        This order ensures that longer, more specific suffixes are matched
        before shorter, more general ones.

        Args:
        word (str): The word to process. Expected to be a valid string
                    containing only alphabetic characters. The word should
                    already be in the desired case (lowercase if case
                    normalization was requested). Must not be None or empty
                    (these conditions should be checked by stem_word()).

        Returns:
        str: The word after applying Step 1a transformations. The returned
                word will have the appropriate suffix removed or modified
                according to the rules above. If no rules apply (word doesn't
                end in 's'), the original word is returned unchanged.

        Examples:
        Standard mode (ORIGINAL):
                'caresses' -> 'caress'  (SSES -> SS rule)
                'ponies' -> 'poni'      (IES -> I rule)
                'dies' -> 'di'          (IES -> I rule)
                'caress' -> 'caress'    (SS -> SS rule, no change)
                'cats' -> 'cat'         (S -> rule)
                'atlas' -> 'atla'       (S -> rule)
                'dog' -> 'dog'          (no rule applies)

        NLTK Extensions mode:
                'dies' -> 'die'         (4-letter IES special case)
                'ties' -> 'tie'         (4-letter IES special case)
                'flies' -> 'fli'        (5 letters, uses standard IES -> I)
                'cries' -> 'cri'        (5 letters, uses standard IES -> I)

        Implementation Notes:
        - This method does not perform input validation as it's a private
        method called by stem_word() which handles validation
        - The method assumes the word parameter is already properly formatted
        - No exceptions are raised directly by this method
        - The NLTK extension check is performed first to override the
        standard IES -> I rule when applicable

        References:
        Porter, M. "An algorithm for suffix stripping."
        Program 14.3 (1980): 130-137.

        NLTK Porter Stemmer implementation:
        https://www.nltk.org/_modules/nltk/stem/porter.html


        note: NLTK doc says:

        "From the paper:

                SSES -> SS                         caresses  ->  caress
                IES  -> I                          ponies    ->  poni
                                            ties      ->  ti
                SS   -> SS                         caress    ->  caress
                S    ->                            cats      ->  cat
        # this NLTK-only rule extends the original algorithm, so
        # that 'flies'->'fli' but 'dies'->'die' etc
        if self.mode == self.NLTK_EXTENSIONS:
                if word.endswith("ies") and len(word) == 4:
                    return self._replace_suffix(word, "ies", "ie")

        return self._apply_rule_list(
                word,
                [
                    ("sses", "ss", None),  # SSES -> SS
                    ("ies", "i", None),  # IES  -> I
                    ("ss", "ss", None),  # SS   -> SS
                    ("s", "", None),  # S    ->
                ],
        )"

        """
        # Apply standard Porter algorithm rules in order of suffix length
        # to ensure longest matches are found first

        # Rule 1: SSES -> SS (remove 'es' from words ending in 'sses')
        if word.endswith("sses"):
            return word[:-2]

        # Check for NLTK extension first - this handles special cases for
        # 4-letter words ending in 'ies' that should become 'ie' rather
        # than 'i' for more intuitive results
        if self.mode == "NLTK_EXTENSIONS" and word.endswith("ies") and len(word) == 4:
            # Remove the 's' to change 'ies' to 'ie'
            # Examples: 'dies' -> 'die', 'ties' -> 'tie'
            return word[:-1]

        # Rule 2: IES -> I (remove 'es' from words ending in 'ies')
        elif word.endswith("ies"):
            return word[:-2]

        # Rule 3: SS -> SS (no change for words ending in 'ss')
        elif word.endswith("ss"):
            return word

        # Rule 4: S -> (remove single 's' at end)
        elif word.endswith("s"):
            return word[:-1]

        # No plural suffix found - return word unchanged
        return word

    def _step1b(self, word: str) -> str:
        """
        Apply Step 1b of the Porter algorithm: Remove past tense suffixes.

        Rules:
        (m>0) EED -> EE (e.g., agreed -> agree)
        (*v*) ED -> (e.g., plastered -> plaster)
        (*v*) ING -> (e.g., motoring -> motor)

        Args:
        word (str): The word to process.

        Returns:
        str: The word after applying Step 1b.
        """
        # Rule: (m>0) EED -> EE
        if word.endswith("eed"):
            stem = word[:-3]
            if self._measure(stem) > 0:
                return stem + "ee"
            return word

        # Rules: (*v*) ED -> and (*v*) ING ->
        flag = False
        if word.endswith("ed"):
            stem = word[:-2]
            if self._contains_vowel(stem):
                word = stem
                flag = True
        elif word.endswith("ing"):
            stem = word[:-3]
            if self._contains_vowel(stem):
                word = stem
                flag = True

        # If ED or ING was removed, apply additional rules
        if flag:
            # AT -> ATE
            if word.endswith("at"):
                return word + "e"
            # BL -> BLE
            elif word.endswith("bl"):
                return word + "e"
            # IZ -> IZE
            elif word.endswith("iz"):
                return word + "e"
            # Double consonant and not ending in L, S, or Z -> single letter
            elif self._ends_with_double_consonant(word):
                last_char = word[-1].lower()
                if last_char not in ("l", "s", "z"):
                    return word[:-1]
            # (m=1 and *o) -> E
            elif self._measure(word) == 1 and self._ends_cvc(word):
                return word + "e"

        return word

    # def _step1c(self, word: str) -> str:
    #     """
    #     Apply Step 1c of the Porter algorithm: Change Y to I.

    #     Original Porter Rule:
    #         (*v*) Y -> I (e.g., happy -> happi, but only if stem contains vowel)

    #     NLTK Extension Rule:
    #         Y -> I only if:
    #         1. Y is preceded by a consonant
    #         2. The stem (without Y) has length > 1

    #     This prevents 'say' -> 'sai' and 'enjoy' -> 'enjoi' in NLTK mode
    #     but allows 'happy' -> 'happi' and 'cry' -> 'cri'

    #     Args:
    #         word (str): The word to process.

    #     Returns:
    #         str: The word after applying Step 1c.
    #     """
    #     if not word.endswith('y'):
    #         return word

    #     stem = word[:-1]

    #     if self.mode == "NLTK_EXTENSIONS":
    #         # NLTK rule: Y -> I only if preceded by consonant and stem length > 1
    #         if len(stem) > 1 and len(word) > 2 and self._is_consonant(word, len(word) - 2):
    #             return stem + 'i'
    #     else:
    #         # Original Porter rule: Y -> I if stem contains vowel
    #         if self._contains_vowel(stem):
    #             return stem + 'i'

    #     return word

    def _step1c(self, word: str) -> str:
        """
        Apply Step 1c of the Porter algorithm: Change Y to I.

        Original Porter Rule:
        (*v*) Y -> I
        Change Y to I if the stem (part before Y) contains a vowel.
        Examples: happy -> happi, sky -> sky

        NLTK Extension Rule:
        Y -> I only if:
        1. Y is preceded by a consonant (not a vowel)
        2. The stem (without Y) has length > 1

        This produces more intuitive results:
        - 'happy' -> 'happi' (Y after consonant, stem length > 1)
        - 'enjoy' -> 'enjoy' (Y after vowel, not changed)
        - 'cry' -> 'cri' (Y after consonant, stem length = 2)
        - 'by' -> 'by' (stem too short)

        Args:
        word (str): The word to process.

        Returns:
        str: The word after applying Step 1c.
        """
        if not word.endswith("y"):
            return word

        stem = word[:-1]

        if self.mode == "NLTK_EXTENSIONS":
            # NLTK rule: Y -> I only if preceded
            # by consonant and stem length > 1
            # This means checking if the last
            # character of the stem is a consonant
            if len(stem) > 1 and self._is_consonant(stem, len(stem) - 1):
                return stem + "i"
        else:
            # Original Porter rule: Y -> I if stem contains any vowel
            if self._contains_vowel(stem):
                return stem + "i"

        return word

    def _step2(self, word: str) -> str:
        """
        Apply Step 2 of the Porter algorithm: Remove derivational suffixes.

        This step has many rules for different suffix patterns.
        All rules require (m>0) for the stem.

        Args:
        word (str): The word to process.

        Returns:
        str: The word after applying Step 2.
        """
        # Define suffix mappings: (suffix, replacement)
        # Note: The C implementation uses 'bli' -> 'ble' as a DEPARTURE from the paper
        # The paper originally specified 'abli' -> 'able'
        # We follow the C implementation for ORIGINAL mode
        suffix_mappings = [
            ("ational", "ate"),
            ("tional", "tion"),
            ("enci", "ence"),
            ("anci", "ance"),
            ("izer", "ize"),
            ("bli", "ble"),  # Martin Porter's DEPARTURE from paper
            ("alli", "al"),
            ("entli", "ent"),
            ("eli", "e"),
            ("ousli", "ous"),
            ("ization", "ize"),
            ("ation", "ate"),
            ("ator", "ate"),
            ("alism", "al"),
            ("iveness", "ive"),
            ("fulness", "ful"),
            ("ousness", "ous"),
            ("aliti", "al"),
            ("iviti", "ive"),
            ("biliti", "ble"),
            ("logi", "log"),  # Martin Porter's DEPARTURE
        ]

        # Try each suffix mapping
        for suffix, replacement in suffix_mappings:
            if word.endswith(suffix):
                stem = word[: -len(suffix)]
                # Check if measure > 0
                if self._measure(stem) > 0:
                    return stem + replacement
                # If measure is not > 0, don't try other suffixes
                break

        return word

    def _step3(self, word: str) -> str:
        """
        Apply Step 3 of the Porter algorithm: Remove derivational suffixes.

        All rules require (m>0) for the stem.

        Args:
        word (str): The word to process.

        Returns:
        str: The word after applying Step 3.
        """
        # Define suffix mappings: (suffix, replacement)
        suffix_mappings = [
            ("icate", "ic"),
            ("ative", ""),
            ("alize", "al"),
            ("iciti", "ic"),
            ("ical", "ic"),
            ("ful", ""),
            ("ness", ""),
        ]

        # Try each suffix mapping
        for suffix, replacement in suffix_mappings:
            if word.endswith(suffix):
                stem = word[: -len(suffix)]
                # Check if measure > 0
                if self._measure(stem) > 0:
                    return stem + replacement
                # If measure is not > 0, don't try other suffixes
                break

        return word

    def _step4(self, word: str) -> str:
        """
        Apply Step 4 of the Porter algorithm: Remove residual suffixes.

        All rules require (m>1) for the stem.

        Args:
        word (str): The word to process.

        Returns:
        str: The word after applying Step 4.
        """
        # Define suffixes to remove (all have empty replacement)
        suffixes_to_remove = [
            "al",
            "ance",
            "ence",
            "er",
            "ic",
            "able",
            "ible",
            "ant",
            "ement",
            "ment",
            "ent",
            "ou",
            "ism",
            "ate",
            "iti",
            "ous",
            "ive",
            "ize",
        ]

        # Special case for 'ion' - requires stem to end in 's' or 't'
        if word.endswith("ion"):
            stem = word[:-3]
            if len(stem) > 0 and stem[-1] in ("s", "t") and self._measure(stem) > 1:
                return stem

        # Try other suffixes
        for suffix in suffixes_to_remove:
            if word.endswith(suffix):
                stem = word[: -len(suffix)]
                # Check if measure > 1
                if self._measure(stem) > 1:
                    return stem
                # If measure is not > 1, don't try other suffixes
                break

        return word

    def _step5a(self, word: str) -> str:
        """
        Apply Step 5a of the Porter algorithm: Remove final 'e'.

        Rules:
        (m>1) E -> (e.g., probate -> probat)
        (m=1 and not *o) E -> (e.g., cease -> ceas)

        Args:
        word (str): The word to process.

        Returns:
        str: The word after applying Step 5a.
        """
        if word.endswith("e"):
            stem = word[:-1]
            measure = self._measure(stem)

            # Rule: (m>1) E ->
            if measure > 1:
                return stem

            # Rule: (m=1 and not *o) E ->
            if measure == 1 and not self._ends_cvc(stem):
                return stem

        return word

    def _step5b(self, word: str) -> str:
        """
        Apply Step 5b of the Porter algorithm: Remove double 'l'.

        Rule:
        (m>1 and *d and *L) -> single letter (e.g., controll -> control)

        Args:
        word (str): The word to process.

        Returns:
        str: The word after applying Step 5b.
        """
        # Check if word ends with double 'l'
        if word.endswith("ll") and self._measure(word[:-1]) > 1:
            return word[:-1]

        return word

    def stem_file_lines(
        self,
        file_path,
        encoding="utf-8",
        errors="strict",
        clean_non_alphanumeric=False,
    ):
        """
        Generator that yields stemmed lines from a file one at a time.

        This method provides memory-efficient processing of large files by
        yielding one stemmed line at a time rather than loading the entire
        file into memory.

        Args:
        file_path (str): Path to the file to process. Must be a valid,
                        readable file path.
        encoding (str): File encoding to use. Default is 'utf-8'.
                    Common alternatives include 'latin-1', 'cp1252'.
        errors (str): How to handle encoding errors. Options:
                    - 'strict': Raise exception (default)
                    - 'ignore': Skip invalid characters
                    - 'replace': Replace with placeholder
        clean_non_alphanumeric (bool): If True, removes punctuation and special
                                     characters before stemming each line.
                                     Default is False.

        Yields:
        str: Stemmed version of each line in the file, preserving
                original line endings and whitespace.

        Raises:
        FileNotFoundError: If file_path doesn't exist
        PermissionError: If lacking read permission
        UnicodeDecodeError: If encoding errors occur (with errors='strict')
        IOError: For other I/O related errors

        Example:
        >>> stemmer = PorterVanillaPyStemmer()
        >>> for stemmed_line in stemmer.stem_file_lines('document.txt'):
        ...     print(stemmed_line, end='')  # end='' because lines include \n

        >>> # Process with different encoding
        >>> for line in stemmer.stem_file_lines('latin_doc.txt', encoding='latin-1'):
        ...     process_line(line)

        >>> # Handle encoding errors gracefully
        >>> for line in stemmer.stem_file_lines('mixed.txt', errors='replace'):
        ...     handle_line(line)
        """
        # import os

        # Validate file exists and is readable before opening
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        if not os.access(file_path, os.R_OK):
            raise PermissionError(f"Cannot read file: {file_path}")

        # Open file with specified encoding and error handling
        try:
            with open(
                file_path, "r", encoding=encoding, errors=errors, buffering=8192
            ) as file_handle:

                # Process file line by line
                for line_number, line in enumerate(file_handle, 1):
                    try:
                        # Stem the line and yield result
                        # stem_document preserves whitespace and punctuation
                        yield self.stem_document(
                            line, clean_non_alphanumeric=clean_non_alphanumeric
                        )

                    except Exception as e:
                        # Wrap any stemming errors with line information
                        raise RuntimeError(
                            f"Error stemming line {line_number} in {file_path}: {e}"
                        ) from e

        except UnicodeDecodeError as e:
            # Enhance error message with file information
            raise UnicodeDecodeError(
                e.encoding, e.object, e.start, e.end, f"{e.reason} in file: {file_path}"
            )

        except IOError as e:
            # Re-raise with more context
            raise IOError(f"Error reading file {file_path}: {e}") from e

    def stem_file_wrapper(
        self,
        filename,
        preserve_case=False,
        output_file=None,
        show_progress=False,
        clean_non_alphanumeric=False,  # ADD THIS PARAMETER
    ):
        """
        Process a text file and output the stemmed version.

        This function processes files line-by-line
        using the stem_file_lines generator
        to handle large files efficiently. It can output to stdout,
        a file, or both,
        and provides progress indication for large files.

        The function uses the PorterVanillaPyStemmer.stem_file_lines()
        generator internally,
        which provides memory-efficient processing by yielding
        one line at a time
        rather than loading the entire file into memory.

        Args:
        filename (str): Path to the input file to process. Must be a valid
                    readable file path. Can be absolute or relative path.
        preserve_case (bool): Whether to preserve original case when stemming.
                            Default is False (convert to lowercase).
                            When True, maintains the case pattern of original words.
        output_file (str, optional): Path to write the stemmed output. If None,
                                output goes to stdout. If provided, creates
                                or overwrites the specified file. Parent
                                directory must exist.
        show_progress (bool): Whether to show progress for large files.
                            Default is True. Progress is shown to stderr to
                            avoid interfering with stdout output. Only shows
                            for files larger than 1MB.
        clean_non_alphanumeric (bool): If True, removes all punctuation, special
                                     characters, and extra whitespace from the text
                                     before stemming. Replaces non-alphanumeric
                                     characters with spaces and normalizes spacing.
                                     Default is False.

                                     Useful for creating searchable text indices
                                     or when punctuation should be ignored.

        Returns:
        None: This function operates via side effects (writing output).

        Raises:
        FileNotFoundError: If the input file doesn't exist
        PermissionError: If lacking read permission for input or write
                            permission for output
        IOError: If other I/O errors occur during processing
        UnicodeDecodeError: If file encoding issues occur
        RuntimeError: If errors occur during stemming process

        Side Effects:
        - Reads from the specified input file
        - Writes to stdout and/or output file
        - May write progress information to stderr
        - Creates or overwrites output file if specified

        Example:
        # Output to stdout with default lowercase stemming
        stem_file_wrapper('document.txt')

        # Save to file with case preservation
        stem_file_wrapper('document.txt', preserve_case=True, output_file='stemmed.txt')

        # Process without progress indicator for automated scripts
        stem_file_wrapper('large_file.txt', show_progress=False)

        # Process with specific output file
        stem_file_wrapper('input.txt', output_file='output.txt')

        Implementation Notes:
        - Uses line-by-line processing for memory efficiency
        - Default buffer size of 8192 bytes for file I/O
        - Progress updates every 1MB or 1000 lines for large files
        - Handles partial processing on interruption
        - UTF-8 encoding with strict error handling
        """
        # import os
        # import sys

        # Validate input file exists and is readable before any processing
        if not os.path.exists(filename):
            print(f"Error: File '{filename}' not found.", file=sys.stderr)
            sys.exit(1)

        if not os.access(filename, os.R_OK):
            print(
                f"Error: Cannot read file '{filename}'. Permission denied.",
                file=sys.stderr,
            )
            sys.exit(1)

        # Get file size for progress reporting if needed
        file_size = os.path.getsize(filename)

        # Validate output file if specified - check before processing
        if output_file:
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                print(
                    f"Error: Output directory '{output_dir}' does not exist.",
                    file=sys.stderr,
                )
                sys.exit(1)

            # Check if we can write to the output location
            try:
                # Try to open for writing (but don't write anything yet)
                with open(output_file, "w", encoding="utf-8") as _:
                    pass
            except PermissionError:
                print(
                    f"Error: Cannot write to '{output_file}'. Permission denied.",
                    file=sys.stderr,
                )
                sys.exit(1)
            except Exception as e:
                print(
                    f"Error: Cannot create output file '{output_file}': {e}",
                    file=sys.stderr,
                )
                sys.exit(1)

        # Print header information to stderr so it doesn't interfere with stdout output
        print(f"Porter Stemmer - File Processing", file=sys.stderr)
        if preserve_case:
            print("(Case preservation enabled)", file=sys.stderr)
        if clean_non_alphanumeric:  # ADD THIS
            print("(Non-alphanumeric cleaning enabled)", file=sys.stderr)
        print(f"Input file: {filename} ({file_size:,} bytes)", file=sys.stderr)
        if output_file:
            print(f"Output file: {output_file}", file=sys.stderr)
        else:
            print("Output: stdout", file=sys.stderr)
        print("=" * 40, file=sys.stderr)

        # Initialize progress tracking variables
        bytes_processed = 0
        lines_processed = 0
        last_progress_update = 0
        output_handle = None

        try:
            # Open output file if specified, with buffering for efficiency
            if output_file:
                output_handle = open(output_file, "w", encoding="utf-8", buffering=8192)

            # Use the stem_file_lines generator to process the file
            # This provides memory-efficient line-by-line processing
            for line_number, stemmed_line in enumerate(
                self.stem_file_lines(
                    filename,
                    encoding="utf-8",
                    errors="strict",
                    clean_non_alphanumeric=clean_non_alphanumeric,
                ),
                start=1,
            ):
                try:
                    # Update progress tracking
                    # Note: We estimate bytes since we can't easily get original line size from generator
                    bytes_processed += len(stemmed_line.encode("utf-8"))
                    lines_processed += 1

                    # Output the stemmed line
                    if output_file:
                        output_handle.write(stemmed_line)
                    else:
                        # Write to stdout without adding extra newline
                        # (stemmed_line already includes original line endings)
                        sys.stdout.write(stemmed_line)
                        sys.stdout.flush()

                    # Show progress for large files (update every MB or 1000 lines)
                    if (
                        show_progress and file_size > 1024 * 1024
                    ):  # Only for files > 1MB
                        if (
                            bytes_processed - last_progress_update > 1024 * 1024
                            or lines_processed % 1000 == 0
                        ):

                            # Estimate progress based on processed bytes
                            # This is approximate since stemmed size may differ from original
                            progress_percent = min(
                                100.0, (bytes_processed / file_size) * 100
                            )
                            print(
                                f"\rProgress: {progress_percent:5.1f}% "
                                f"({lines_processed:,} lines processed)",
                                end="",
                                file=sys.stderr,
                            )
                            last_progress_update = bytes_processed

                except Exception as e:
                    # This shouldn't happen as stem_file_lines handles errors,
                    # but we include it for completeness
                    print(
                        f"\nError processing line {line_number}: {e}", file=sys.stderr
                    )
                    # Attempt to continue with next line
                    continue

            # Clear progress line if it was shown
            if show_progress and file_size > 1024 * 1024:
                print("\r" + " " * 60 + "\r", end="", file=sys.stderr)

            # Success message with statistics
            print("\nProcessing complete:", file=sys.stderr)
            print(f"  Lines processed: {lines_processed:,}", file=sys.stderr)
            print(
                f"  Bytes processed: {bytes_processed:,} (estimated)", file=sys.stderr
            )

            if output_file:
                print(f"  Output written to: {output_file}", file=sys.stderr)
                output_size = os.path.getsize(output_file)
                print(f"  Output file size: {output_size:,} bytes", file=sys.stderr)

        except FileNotFoundError as e:
            # This can happen if file is deleted during processing
            print(
                f"""\nError: File '{filename}' not found 
                or deleted in processing.{str(e)}""",
                file=sys.stderr,
            )
            sys.exit(1)

        except PermissionError as e:
            # This can happen if permissions change during processing
            print(f"\nError: Permission denied while processing: {e}", file=sys.stderr)
            sys.exit(1)

        except UnicodeDecodeError as e:
            # This comes from stem_file_lines when encoding issues occur
            print(f"\nError: File encoding issue - {e}", file=sys.stderr)
            print(
                "Try using a different encoding or check file format.", file=sys.stderr
            )
            sys.exit(1)

        except RuntimeError as e:
            # This comes from stem_file_lines when stemming errors occur
            print(f"\nError during stemming: {e}", file=sys.stderr)
            sys.exit(1)

        except KeyboardInterrupt:
            # Handle user interruption gracefully
            print("\n\nProcessing interrupted by user.", file=sys.stderr)
            print(
                f"Processed {lines_processed:,} lines before interruption.",
                file=sys.stderr,
            )
            if output_file and output_handle:
                print(
                    f"Partial output may be available in: {output_file}",
                    file=sys.stderr,
                )
            sys.exit(1)

        except MemoryError:
            # shouldn't happen with line-by-line processing, but just in case
            print("\nError: Out of memory while processing file.", file=sys.stderr)
            print(f"Processed {lines_processed:,} lines before error.", file=sys.stderr)
            sys.exit(1)

        except Exception as e:
            # Catch-all for any unexpected errors
            print(f"\nUnexpected error during file processing: {e}", file=sys.stderr)
            # import traceback
            traceback.print_exc(file=sys.stderr)
            sys.exit(1)

        finally:
            # Ensure output file is closed even if errors occur
            if output_handle:
                try:
                    output_handle.close()
                except Exception as e:
                    # Ignore errors during cleanup
                    print(f"no output_handle from stem_file_wrapper {str(e)}")
                    pass

    # def stem_file_simple(self, input_filename, output_filename):
    #     """
    #     Read a file, stem all words, write to output file.
    #     """
    #     try:
    #         # Read the entire file
    #         with open(input_filename, 'r', encoding='utf-8') as f:
    #             text = f.read()

    #         # Stem the text
    #         stemmed_text = self.stem_document(text)

    #         # Write to output file
    #         with open(output_filename, 'w', encoding='utf-8') as f:
    #             f.write(stemmed_text)
    #     except Exception as e:
    #         print(str(e))
    #         traceback.print_exc(file=sys.stderr)
    #         sys.exit(1)

    ######################################
    # End of vanilla porter stemmer class
    ######################################


def run_comprehensive_tests():
    """
    Run comprehensive tests of the Porter Stemmer implementation.

    This test suite verifies the Porter Stemmer against correct expected outputs
    for both ORIGINAL and NLTK_EXTENSIONS modes.

    Returns:
        bool: True if all tests pass, False if any test fails
    """
    print("Porter Stemmer - Comprehensive Test Suite")
    print("=" * 70)
    print()

    # Run tests for both modes
    original_passed = test_original_mode()
    print("\n" + "=" * 70 + "\n")
    nltk_passed = test_nltk_extensions_mode()
    print("\n" + "=" * 70 + "\n")
    error_handling_passed = test_error_handling()
    print("\n" + "=" * 70 + "\n")
    misc_features_passed = test_miscellaneous_features()
    print("\n" + "=" * 70 + "\n")
    alphanumeric_cleaning_passed = test_alphanumeric_cleaning()

    # Summary
    all_passed = (
        original_passed
        and nltk_passed
        and error_handling_passed
        and misc_features_passed
        and alphanumeric_cleaning_passed
    )

    print("\n" + "=" * 70)
    print("\nOVERALL TEST SUMMARY:")
    print(f"Original Mode Tests: {'PASSED' if original_passed else 'FAILED'}")
    print(f"NLTK Extensions Mode Tests: {'PASSED' if nltk_passed else 'FAILED'}")
    print(f"Error Handling Tests: {'PASSED' if error_handling_passed else 'FAILED'}")
    print(
        f"Miscellaneous Features Tests: {'PASSED' if misc_features_passed else 'FAILED'}"
    )
    print(
        f"Alphanumeric Cleaning Tests: {'PASSED' if alphanumeric_cleaning_passed else 'FAILED'}"
    )  # ADD THIS LINE
    print(f"\nAll Tests: {'PASSED' if all_passed else 'FAILED'}")
    print("=" * 70)

    return all_passed


def test_alphanumeric_cleaning():
    """
    Test the non-alphanumeric character cleaning and space normalization feature.

    This tests the _clean_non_alphanumeric_characters_and_normalize_spaces method
    and the clean_non_alphanumeric parameter in stem_document.

    Returns:
        bool: True if all tests pass, False if any fail
    """
    print("TESTING NON-ALPHANUMERIC CLEANING FEATURE")
    print("-" * 70)

    passed = True
    stemmer = PorterVanillaPyStemmer()

    # Test the private cleaning method directly
    print("\nTesting _clean_non_alphanumeric_characters_and_normalize_spaces:")
    print("-" * 50)

    cleaning_test_cases = [
        # (input, expected_output, description)
        ("Hello, world!", "Hello world", "Basic punctuation removal"),
        ("user@email.com", "user email com", "Email address cleaning"),
        ("Phone: (555) 123-4567", "Phone 555 123 4567", "Phone number cleaning"),
        ("don't", "don't", "Apostrophe handling"),
        ("pre-process", "pre process", "Hyphen handling"),
        ("Hello\n\tWorld", "Hello World", "Whitespace normalization"),
        (
            "Multiple   spaces    here",
            "Multiple spaces here",
            "Multiple space normalization",
        ),
        ("  Leading and trailing  ", "Leading and trailing", "Trim spaces"),
        ("Special@#$%^&*()chars!", "Special chars", "Special character removal"),
        ("Mix123Numbers456", "Mix123Numbers456", "Alphanumeric preserved"),
        ("", "", "Empty string handling"),
        ("!!!", "", "Only punctuation becomes empty"),
        ("one\ntwo\tthree\rfour", "one two three four", "Various whitespace chars"),
        ("UTF-8: café résumé", "UTF 8 café résumé", "Non-ASCII character handling"),
    ]

    for input_text, expected, description in cleaning_test_cases:
        try:
            actual = stemmer._clean_non_alphanumeric_characters_and_normalize_spaces(
                input_text
            )
            if actual == expected:
                print(f"✓ {description:30} | '{input_text}' -> '{actual}'")
            else:
                print(f"✗ {description:30} | '{input_text}'")
                print(f"  Expected: '{expected}'")
                print(f"  Actual:   '{actual}'")
                passed = False
        except Exception as e:
            print(f"✗ {description:30} | ERROR: {str(e)}")
            passed = False

    # Test stem_document with cleaning enabled
    print("\n\nTesting stem_document with clean_non_alphanumeric=True:")
    print("-" * 50)

    document_test_cases = [
        # (input, expected_output, description)
        (
            "The user's e-mail is: john@example.com!",
            "the user's e mail is john exampl com",
            "Email and punctuation in document",
        ),
        (
            "Running, flying & swimming (quickly)!",
            "run fly swim quickli",
            "Multiple words with punctuation",
        ),
        (
            "Don't forget: pre-process the data!",
            "don't forget pre process the data",
            "Contractions and hyphens",
        ),
        (
            "Phone: (555) 123-4567\nAddress: 123 Main St.",
            "phone 555 123 4567 address 123 main st",
            "Multi-line with numbers",
        ),
        (
            "Testing   multiple    spaces   here!",
            "test multipl space here",
            "Multiple spaces with stemming",
        ),
        (
            "UPPERCASE, lowercase, MiXeD-CaSe!",
            "uppercas lowercas mix case",
            "Case handling with cleaning",
        ),
    ]

    for input_text, expected, description in document_test_cases:
        try:
            actual = stemmer.stem_document(input_text, clean_non_alphanumeric=True)
            if actual == expected:
                print(f"✓ {description}")
            else:
                print(f"✗ {description}")
                print(f"  Input:    '{input_text}'")
                print(f"  Expected: '{expected}'")
                print(f"  Actual:   '{actual}'")
                passed = False
        except Exception as e:
            print(f"✗ {description} | ERROR: {str(e)}")
            passed = False

    # Test comparison: with and without cleaning
    print("\n\nComparing stem_document with and without cleaning:")
    print("-" * 50)

    comparison_text = "The user's e-mail is: test@example.com (urgent)!"

    without_cleaning = stemmer.stem_document(
        comparison_text, clean_non_alphanumeric=False
    )
    with_cleaning = stemmer.stem_document(comparison_text, clean_non_alphanumeric=True)

    print(f"Original text:    '{comparison_text}'")
    print(f"Without cleaning: '{without_cleaning}'")
    print(f"With cleaning:    '{with_cleaning}'")

    # Verify the difference is as expected
    if "'" in without_cleaning and "@" in without_cleaning:
        print("✓ Without cleaning preserves punctuation")
    else:
        print("✗ Without cleaning should preserve punctuation")
        passed = False

    if ":" not in with_cleaning and "@" not in with_cleaning:
        print("✓ With cleaning removes punctuation")
    else:
        print("✗ With cleaning should remove punctuation")
        passed = False

    # Test edge cases
    print("\n\nTesting edge cases:")
    print("-" * 50)

    # Test with only non-alphanumeric characters
    only_punct = "!!!@@@###$$$"
    result = stemmer.stem_document(only_punct, clean_non_alphanumeric=True)
    if result == "":
        print("✓ Only punctuation returns empty string")
    else:
        print(f"✗ Only punctuation should return empty string, got: '{result}'")
        passed = False

    # Test edge cases
    print("\n\nTesting edge cases:")
    print("-" * 50)

    # Test with only non-alphanumeric characters
    only_punct = "!!!@@@###$$$"
    result = stemmer.stem_document(only_punct, clean_non_alphanumeric=True)
    if result == "":
        print("✓ Only punctuation returns empty string")
    else:
        print(f"✗ Only punctuation should return empty string, got: '{result}'")
        passed = False

    # Test with Unicode characters - now with proper verification
    print("\nTesting Unicode character preservation:")
    unicode_test_cases = [
        # (input, expected, description)
        ("Café résumé naïve", "café résumé naïv", "French accented characters"),
        ("Zürich München", "zürich münchen", "German umlauts"),
        ("Москва Санкт-Петербург", "москва санкт петербург", "Cyrillic script"),
        ("北京 上海", "北京 上海", "Chinese characters"),
        ("Hello café-society!", "hello café societi", "Mixed ASCII and Unicode"),
    ]

    for input_text, expected, description in unicode_test_cases:
        result = stemmer.stem_document(input_text, clean_non_alphanumeric=True)
        if result == expected:
            print(f"✓ {description}: '{input_text}' -> '{result}'")
        else:
            print(f"✗ {description}:")
            print(f"  Input:    '{input_text}'")
            print(f"  Expected: '{expected}'")
            print(f"  Actual:   '{result}'")
            passed = False

    # Summary
    print(
        f"\n\nAlphanumeric Cleaning Feature Summary: {'PASSED' if passed else 'FAILED'}"
    )
    return passed


def test_original_mode():
    """
    Test the Porter Stemmer in ORIGINAL mode.

    This tests the implementation against the original Porter algorithm
    as published in the 1980 paper.

    Returns:
        bool: True if all tests pass, False if any fail
    """
    print("TESTING ORIGINAL PORTER ALGORITHM MODE")
    print("-" * 70)

    # Test tracking
    total_tests = 0
    passed_tests = 0
    failed_tests = []

    def test_case(description: str, word: str, expected: str) -> bool:
        """Execute a single test case."""
        nonlocal total_tests, passed_tests, failed_tests
        total_tests += 1

        actual = stemmer.stem_word(word)
        if actual == expected:
            passed_tests += 1
            print(f"✓ {word:15} -> {actual:15} ({description})")
            return True
        else:
            failed_tests.append(
                {
                    "word": word,
                    "expected": expected,
                    "actual": actual,
                    "description": description,
                }
            )
        print(f"✗ {word:15} -> {actual:15} Expected: {expected:15} ({description})")
        return False

    # Create stemmer in ORIGINAL mode
    stemmer = PorterVanillaPyStemmer(mode="ORIGINAL")

    # Test Step 1a - Plurals
    print("\nStep 1a - Plural Removal:")
    test_case("SSES -> SS", "caresses", "caress")
    test_case("IES -> I", "ponies", "poni")
    test_case("IES -> I", "ties", "ti")
    test_case("IES -> I", "dies", "di")
    test_case("SS -> SS", "caress", "caress")
    test_case("S -> ''", "cats", "cat")

    # Test Step 1b - Past tense
    print("\nStep 1b - Past Tense Removal:")
    test_case("(m>0) EED -> EE", "agreed", "agre")
    test_case("(m=0) EED -> EED", "feed", "feed")
    test_case("(*v*) ED -> ''", "plastered", "plaster")
    test_case("No vowel in stem", "bled", "bled")
    test_case("(*v*) ING -> ''", "motoring", "motor")
    test_case("Double consonant", "hopping", "hop")
    test_case("CVC -> +E", "filing", "file")

    # Test Step 1c - Y to I
    print("\nStep 1c - Y to I Conversion:")
    test_case("(*v*) Y -> I", "happy", "happi")
    test_case("No vowel in stem", "cry", "cry")
    test_case("Y after vowel", "say", "sai")
    test_case("Y after vowel", "enjoy", "enjoi")

    # Test Step 2 - Derivational suffixes
    print("\nStep 2 - Derivational Suffixes:")
    test_case("ATIONAL -> ATE", "relational", "relat")
    test_case("TIONAL -> TION", "conditional", "condit")
    test_case("ENCI -> ENCE", "valenci", "valenc")
    test_case("IZER -> IZE", "digitizer", "digit")
    test_case(
        "BLI -> BLE", "conformabli", "conform"
    )  # CORRECTED: Original mode now uses BLI->BLE
    test_case("IZATION -> IZE", "vietnamization", "vietnam")

    # Test Step 3
    print("\nStep 3 - More Derivational Suffixes:")
    test_case("ICATE -> IC", "triplicate", "triplic")
    test_case("ATIVE -> ''", "formative", "form")
    test_case("ALIZE -> AL", "formalize", "formal")
    test_case("ICITI -> IC", "electriciti", "electr")
    test_case("FUL -> ''", "hopeful", "hope")

    # Test Step 4
    print("\nStep 4 - Residual Suffixes:")
    test_case("AL -> ''", "revival", "reviv")
    test_case("ER -> ''", "airliner", "airlin")
    test_case("ABLE -> ''", "adjustable", "adjust")
    test_case("MENT -> ''", "adjustment", "adjust")
    test_case("(S/T)ION -> ''", "adoption", "adopt")

    # Test Step 5
    print("\nStep 5 - Final E and LL:")
    test_case("(m>1) E -> ''", "probate", "probat")
    test_case("(m=1, not *o) E -> ''", "cease", "ceas")
    test_case("(m>1) LL -> L", "controll", "control")

    # Special words
    print("\nSpecial Words (Original Mode):")
    test_case("Special word", "sky", "sky")
    test_case("Special word", "skies", "sky")
    test_case("Special word", "news", "news")
    test_case("Special word", "innings", "inning")
    test_case(
        "NOT special", "dying", "dy"
    )  # CORRECTED: Step1b removes 'ing', no vowel in 'd' so Y stays
    test_case(
        "NOT special", "lying", "ly"
    )  # CORRECTED: Step1b removes 'ing', no vowel in 'l' so Y stays
    test_case(
        "NOT special", "tying", "ty"
    )  # Step1b removes 'ing', no vowel in 't' so Y stays

    # Summary
    print(f"\nOriginal Mode Summary: {passed_tests}/{total_tests} tests passed")
    if failed_tests:
        print(f"Failed tests: {len(failed_tests)}")
        for fail in failed_tests[:5]:
            print(
                f"""  - {fail['word']}: expected '{fail['expected']}', 
                  got '{fail['actual']}'"""
            )

    return len(failed_tests) == 0


def test_nltk_extensions_mode():
    """
    Test the Porter Stemmer in NLTK_EXTENSIONS mode.

    This tests the implementation with NLTK's improvements to the algorithm.

    Returns:
        bool: True if all tests pass, False if any fail
    """
    print("TESTING NLTK EXTENSIONS MODE")
    print("-" * 70)

    # Test tracking
    total_tests = 0
    passed_tests = 0
    failed_tests = []

    def test_case(description: str, word: str, expected: str) -> bool:
        """Execute a single test case."""
        nonlocal total_tests, passed_tests, failed_tests
        total_tests += 1

        actual = stemmer.stem_word(word)
        if actual == expected:
            passed_tests += 1
            print(f"✓ {word:15} -> {actual:15} ({description})")
            return True
        else:
            failed_tests.append(
                {
                    "word": word,
                    "expected": expected,
                    "actual": actual,
                    "description": description,
                }
            )
        print(f"✗ {word:15} -> {actual:15} Expected: {expected:15} ({description})")
        return False

    # Create stemmer in NLTK_EXTENSIONS mode
    stemmer = PorterVanillaPyStemmer(mode="NLTK_EXTENSIONS")

    # Test NLTK-specific Step 1a behavior
    print("\nStep 1a - NLTK 4-letter IES rule:")
    test_case("4-letter IES -> IE", "dies", "die")
    test_case("4-letter IES -> IE", "ties", "tie")
    test_case("4-letter IES -> IE", "lies", "lie")
    test_case("5-letter IES -> I", "flies", "fli")
    test_case("6-letter IES -> I", "cries", "cri")

    # Test NLTK-specific Step 1c behavior
    print("\nStep 1c - NLTK Y to I rule:")
    test_case("Y -> I (consonant before)", "happy", "happi")
    test_case("Y -> I (NLTK rule)", "cry", "cri")  # Length > 1, preceded by consonant
    test_case(
        "Y stays (after vowel)", "say", "say"
    )  # CORRECTED: NLTK doesn't change Y after vowel
    test_case(
        "Y stays (after vowel)", "enjoy", "enjoy"
    )  # CORRECTED: NLTK doesn't change Y after vowel
    test_case("Y stays (too short)", "by", "by")  # Stem 'b' has length 1, so Y stays

    # Test special words pool
    print("\nNLTK Special Words Pool:")
    test_case("Special: dying", "dying", "die")
    test_case("Special: lying", "lying", "lie")
    test_case("Special: tying", "tying", "tie")
    test_case("Special: dies", "dies", "die")  # Also handled by 4-letter rule
    test_case("Special: news", "news", "news")
    test_case("Special: innings", "innings", "inning")

    # Test short word handling
    print("\nShort Word Handling (words <= 2 chars unchanged):")
    test_case("2-letter word", "am", "am")
    test_case("2-letter word", "is", "is")
    test_case("1-letter word", "a", "a")

    # Summary
    print(f"\nNLTK Extensions Mode Summary: {passed_tests}/{total_tests} tests passed")
    if failed_tests:
        print(f"Failed tests: {len(failed_tests)}")
        for fail in failed_tests[:5]:
            print(
                f"  - {fail['word']}: expected '{fail['expected']}', got '{fail['actual']}'"
            )

    return len(failed_tests) == 0


def test_error_handling():
    """
    Test error handling and edge cases.

    Returns:
        bool: True if all tests pass, False if any fail
    """
    print("TESTING ERROR HANDLING")
    print("-" * 70)

    passed = True
    stemmer = PorterVanillaPyStemmer()

    # Test None input
    print("\nTesting None input:")
    try:
        stemmer.stem_word(None)
        print("✗ None input should raise ValueError")
        passed = False
    except ValueError:
        print("✓ None input raises ValueError as expected")
    except Exception as e:
        print(f"✗ None input raised unexpected {type(e).__name__}: {e}")
        passed = False

    # Test non-string input
    print("\nTesting non-string input:")
    try:
        stemmer.stem_word(123)
        print("✗ Integer input should raise TypeError")
        passed = False
    except TypeError:
        print("✓ Integer input raises TypeError as expected")
    except Exception as e:
        print(f"✗ Integer input raised unexpected {type(e).__name__}: {e}")
        passed = False

    # Test empty string
    print("\nTesting empty string:")
    try:
        stemmer.stem_word("")
        print("✗ Empty string should raise ValueError")
        passed = False
    except ValueError:
        print("✓ Empty string raises ValueError as expected")
    except Exception as e:
        print(f"✗ Empty string raised unexpected {type(e).__name__}: {e}")
        passed = False

    # Test document processing with None
    print("\nTesting document processing with None:")
    try:
        stemmer.stem_document(None)
        print("✗ None document should raise ValueError")
        passed = False
    except ValueError:
        print("✓ None document raises ValueError as expected")
    except Exception as e:
        print(f"✗ None document raised unexpected {type(e).__name__}: {e}")
        passed = False

    # Test token list with invalid input
    print("\nTesting token list with non-list:")
    try:
        stemmer.stem_tokens("not a list")
        print("✗ Non-list input should raise TypeError")
        passed = False
    except TypeError:
        print("✓ Non-list input raises TypeError as expected")
    except Exception as e:
        print(f"✗ Non-list input raised unexpected {type(e).__name__}: {e}")
        passed = False

    print(f"\nError Handling Summary: {'PASSED' if passed else 'FAILED'}")
    return passed


def test_miscellaneous_features():
    """
    Test miscellaneous features like case preservation and document processing.

    Returns:
        bool: True if all tests pass, False if any fail
    """
    print("TESTING MISCELLANEOUS FEATURES")
    print("-" * 70)

    passed = True

    # Test case preservation
    print("\nTesting case preservation:")
    case_stemmer = PorterVanillaPyStemmer(to_lowercase=False)

    test_cases = [
        ("Running", "Run"),
        ("FLIES", "FLI"),
        ("HaPpIlY", "HaPpIlI"),
    ]

    for word, expected in test_cases:
        actual = case_stemmer.stem_word(word)
        if actual == expected:
            print(f"✓ {word} -> {actual} (case preserved)")
        else:
            print(f"✗ {word} -> {actual}, expected {expected}")
            passed = False

    # Test document processing
    print("\nTesting document processing:")
    stemmer = PorterVanillaPyStemmer()

    test_doc = "The boys are running quickly!"
    expected = "the boi ar run quickli!"
    actual = stemmer.stem_document(test_doc)

    if actual == expected:
        print("✓ Document processing works correctly")
    else:
        print(f"✗ Document processing failed")
        print(f"  Expected: {expected}")
        print(f"  Actual:   {actual}")
        passed = False

    # Test token list processing
    print("\nTesting token list processing:")
    tokens = ["running", "flies", "happily"]
    expected = ["run", "fli", "happili"]
    actual = stemmer.stem_tokens(tokens)

    if actual == expected:
        print("✓ Token list processing works correctly")
    else:
        print(f"✗ Token list processing failed")
        print(f"  Expected: {expected}")
        print(f"  Actual:   {actual}")
        passed = False

    print(f"\nMiscellaneous Features Summary: {'PASSED' if passed else 'FAILED'}")
    return passed


# Example usage and basic testing
if __name__ == "__main__":
    # import sys

    # Define the example code as a string for easy display
    example_code = '''
################################
# Porter Stemmer Module Example
################################

# note: this assumes vanilla_porter_stemmer_module.py is the file name

# import from module
from vanilla_porter_stemmer_module import PorterVanillaPyStemmer

# Create a stemmer instance with default settings (converts to lowercase)
stemmer = PorterVanillaPyStemmer()

# Create a stemmer that preserves original case
case_preserving_stemmer = PorterVanillaPyStemmer(to_lowercase=False)

# stem one word - default behavior (lowercase)
result = stemmer.stem_word('Fishes')
print(f"Default (lowercase): 'Fishes' -> '{result}'")

# stem same word - preserving case
result_preserved = case_preserving_stemmer.stem_word('Fishes')
print(f"Preserve case: 'Fishes' -> '{result_preserved}'")

print("\\n" + "=" * 50 + "\\n")

# Test individual words
test_words = [
    "running", "flies", "happily", "caresses", "ponies", "cats",
    "agreed", "plastered", "motoring", "hoping", "hopping",
    "fizzed", "failing", "filing", "happy", "sky", "relational",
    "conditional", "vilely", "analogously", "vietnamization",
    "predication", "operator", "feudalism", "decisiveness",
    "hopefulness", "callousness", "formality", "sensitivity",
    "sensibility"
]

print("Individual word stemming examples:")
print("-" * 50)
for word in test_words:
    stemmed = stemmer.stem_word(word)
    print(f"{word:20} -> {stemmed}")

print("\\n" + "=" * 50 + "\\n")

# Test document processing
test_document = """
The boys are running quickly through the fields. 
They were hoping to catch butterflies, but the flies 
kept bothering them. Happily, they enjoyed their day anyway!
"""

print("Document stemming example:")
print("-" * 50)
print("Original:")
print(test_document)
print("\\nStemmed:")
print(stemmer.stem_document(test_document))

print("\\n" + "=" * 50 + "\\n")

# Test token list processing
tokens = ["The", "children", "were", "playing", "happily", "outside"]
stemmed_tokens = stemmer.stem_tokens(tokens)

print("Token list stemming example:")
print("-" * 50)
print("Original tokens:", tokens)
print("Stemmed tokens: ", stemmed_tokens)

# Example with case preservation
print("\\nWith case preservation:")
stemmed_tokens_case = case_preserving_stemmer.stem_tokens(tokens)
print("Original tokens:", tokens)
print("Stemmed tokens: ", stemmed_tokens_case)
    '''

    def print_usage_help():
        """
        Print clear usage instructions for the module.

        This function displays all available command-line options
        with examples of how to use them.
        """
        help_text = """
Porter Stemmer - Command Line Usage
===================================

Available options:
--help, -h              Show this help message
--example               Show example Python code for using the stemmer
--demo                  Run a live demonstration
--test                  Run comprehensive test suite
--word WORD [WORD ...]  Stem one or more words
--file FILENAME         Process a text file and output stemmed version
--preserve-case         Preserve original case (default: convert to lowercase)
--clean-non-alpha       Remove punctuation and special characters before stemming


Examples:
python porter_stemmer.py --help
python porter_stemmer.py --example
python porter_stemmer.py --demo
python porter_stemmer.py --test
python porter_stemmer.py --word running flies happy
python porter_stemmer.py --word Running Flies Happy --preserve-case
python porter_stemmer.py --file document.txt
python porter_stemmer.py --file document.txt --preserve-case
      """
        print(help_text)

    def print_example_code():
        """
        Display example code showing how to use the Porter Stemmer.

        This prints Python code examples that users can copy and modify
        for their own use cases.
        """
        print("Porter Stemmer - Example Code")
        print("=" * 60)
        print("\nYou can copy and use this code in your own Python scripts:\n")
        print(example_code)
        print("\n" + "=" * 60)

    def run_live_demo(preserve_case=False):
        """
        Run a live demonstration of the Porter Stemmer functionality.

        This function provides a comprehensive demonstration of the Porter Stemmer's
        capabilities by showing various use cases including individual word stemming,
        document processing, and token list handling. The demonstration includes
        both case-preserving and lowercase modes.

        The demonstration covers:
            - Basic word stemming with case handling comparison
            - Individual word examples showing various stemming rules
            - Full document processing preserving punctuation and formatting
            - Token list processing for pre-tokenized text
            - Case preservation examples

        Args:
            preserve_case (bool): If True, demonstrates case-preserving stemming.
                                If False (default), demonstrates standard lowercase
                                stemming. This affects how the demonstration presents
                                the examples but shows both modes regardless.

        Returns:
            None: This function prints output directly to stdout and does not
                return any value.

        Raises:
            Exception: Any exceptions from the PorterVanillaPyStemmer are caught and
                    displayed as part of the demonstration to show error handling.

        Side Effects:
            Prints demonstration output to stdout showing various stemming examples
            and use cases.

        Example:
            >>> run_live_demo()  # Run standard demonstration
            >>> run_live_demo(preserve_case=True)  # Run with case preservation focus

        Notes:
            This function is designed for interactive demonstration and learning.
            It shows real-world usage patterns and helps users understand how
            to integrate the Porter Stemmer into their own code.
        """
        # Print demonstration header with clear indication of mode
        print("Porter Stemmer - Live Demonstration")
        if preserve_case:
            print("(Case preservation mode highlighted)")
        print("=" * 60)
        print()

        try:
            # Create stemmer instances for demonstration
            # We create both types to show the difference
            lowercase_stemmer = PorterVanillaPyStemmer(to_lowercase=True)
            case_preserving_stemmer = PorterVanillaPyStemmer(to_lowercase=False)

            # Section 1: Basic case handling demonstration
            print("1. Case Handling Demonstration")
            print("-" * 50)

            # Define test word for case demonstration
            case_demo_word = "Fishes"

            # Demonstrate lowercase stemming (default behavior)
            lowercase_result = lowercase_stemmer.stem_word(case_demo_word)
            print(f"Default (lowercase): '{case_demo_word}' -> '{lowercase_result}'")

            # Demonstrate case-preserving stemming
            case_preserved_result = case_preserving_stemmer.stem_word(case_demo_word)
            print(f"Preserve case: '{case_demo_word}' -> '{case_preserved_result}'")

            print("\n" + "=" * 50 + "\n")

            # Section 2: Individual word stemming examples
            print("2. Individual Word Stemming Examples")
            print("-" * 50)

            # Comprehensive list of test words demonstrating various rules
            test_words_for_demonstration = [
                # Step 1a examples (plurals)
                "running",
                "flies",
                "happily",
                "caresses",
                "ponies",
                "cats",
                # Step 1b examples (past tense)
                "agreed",
                "plastered",
                "motoring",
                "hoping",
                "hopping",
                # Various suffixes
                "fizzed",
                "failing",
                "filing",
                "happy",
                "sky",
                "relational",
                "conditional",
                "vilely",
                "analogously",
                "vietnamization",
                "predication",
                "operator",
                "feudalism",
                "decisiveness",
                "hopefulness",
                "callousness",
                "formality",
                "sensitivity",
                "sensibility",
            ]

            # Choose which stemmer to use based on demonstration mode
            demo_stemmer = (
                case_preserving_stemmer if preserve_case else lowercase_stemmer
            )

            # Process and display each word
            for word_to_stem in test_words_for_demonstration:
                try:
                    stemmed_result = demo_stemmer.stem_word(word_to_stem)
                    print(f"{word_to_stem:20} -> {stemmed_result}")
                except Exception as word_error:
                    # Show error handling in action
                    print(f"{word_to_stem:20} -> ERROR: {str(word_error)}")

            print("\n" + "=" * 50 + "\n")

            # Section 3: Document processing demonstration
            print("3. Document Stemming Example")
            print("-" * 50)

            # Multi-line test document with various words and punctuation
            test_document_text = """The boys are running quickly through the fields. ice
cream. They were hoping to catch butterflies but can't, but the flies 
kept bothering them. Happily, they enjoyed their day anyway!"""

            print("Original:")
            print(test_document_text)

            # Process the document
            try:
                stemmed_document = demo_stemmer.stem_document(test_document_text)
                print("\nStemmed:")
                print(stemmed_document)
            except Exception as doc_error:
                print(f"\nError processing document: {str(doc_error)}")

            # Process the document
            try:
                stemmed_document = demo_stemmer.stem_document(
                    test_document_text,
                    clean_non_alphanumeric=True,
                )
                print("\nStemmed & Cleaned:")
                print(stemmed_document)
            except Exception as doc_error:
                print(f"\nError processing document: {str(doc_error)}")

            print("\n" + "=" * 50 + "\n")

            # Section 4: Token list processing demonstration
            print("4. Token List Stemming Example")
            print("-" * 50)

            # Example token list with mixed case
            demonstration_tokens = [
                "The",
                "children",
                "were",
                "playing",
                "happily",
                "outside",
            ]

            # Process with lowercase stemmer
            print("With lowercase stemming:")
            print(f"Original tokens: {demonstration_tokens}")
            try:
                lowercase_stemmed_tokens = lowercase_stemmer.stem_tokens(
                    demonstration_tokens
                )
                print(f"Stemmed tokens:  {lowercase_stemmed_tokens}")
            except Exception as token_error:
                print(f"Error processing tokens: {str(token_error)}")

            # Process with case-preserving stemmer
            print("\nWith case preservation:")
            print(f"Original tokens: {demonstration_tokens}")
            try:
                case_preserved_tokens = case_preserving_stemmer.stem_tokens(
                    demonstration_tokens
                )
                print(f"Stemmed tokens:  {case_preserved_tokens}")
            except Exception as token_error:
                print(f"Error processing tokens: {str(token_error)}")

            print("\n" + "=" * 50 + "\n")

            # Section 5: Special cases and edge cases
            print("5. Special Cases Demonstration")
            print("-" * 50)

            # Demonstrate handling of special words
            special_test_words = ["sky", "skies", "news", "dying", "lying"]

            print("Special word handling:")
            for special_word in special_test_words:
                try:
                    special_stemmed = demo_stemmer.stem_word(special_word)
                    print(f"{special_word:15} -> {special_stemmed}")
                except Exception as special_error:
                    print(f"{special_word:15} -> ERROR: {str(special_error)}")

            # Demonstrate very short words
            print("\nShort word handling (2 letters or less):")
            short_words = ["am", "is", "be", "we", "at", "I", "a"]
            for short_word in short_words:
                try:
                    short_stemmed = demo_stemmer.stem_word(short_word)
                    print(f"{short_word:15} -> {short_stemmed}")
                except Exception as short_error:
                    print(f"{short_word:15} -> ERROR: {str(short_error)}")

            print("\n" + "=" * 60)
            print("Demonstration completed successfully!")

        except Exception as unexpected_error:
            # Catch any unexpected errors at the top level
            print(f"\nUnexpected error during demonstration: {str(unexpected_error)}")
            print("Please report this error for investigation.")
            # In production, we might want to log this with more detail
            # import traceback
            print("\nDebug information:")
            print(traceback.format_exc())

    def stem_words_from_args(word_list, preserve_case=False):
        """
        Stem a list of words provided as command-line arguments.

        Args:
            word_list (list): List of words to stem
            preserve_case (bool): Whether to preserve original case

        This function creates a stemmer instance and processes each
        word, showing the original and stemmed versions.
        """
        print("Porter Stemmer - Word Processing")
        if preserve_case:
            print("(Case preservation enabled)")
        print("=" * 40)

        # Create stemmer instance with appropriate case handling
        stemmer = PorterVanillaPyStemmer(to_lowercase=not preserve_case)

        # Process each word
        for word in word_list:
            try:
                stemmed = stemmer.stem_word(word)
                print(f"{word:20} -> {stemmed}")
            except Exception as error:
                print(f"Error processing '{word}': {error}")

    ###############################
    # Parse command-line arguments
    ###############################

    # Get all arguments except the script name
    args = sys.argv[1:]

    # Check for preserve-case flag early
    # This flag can be used with other options
    preserve_case = "--preserve-case" in args
    if preserve_case:
        # Remove the flag from args so it doesn't interfere with other processing
        args.remove("--preserve-case")

    # If no arguments provided (after removing preserve-case), show help
    if not args:
        print_usage_help()
        sys.exit(0)

    # Check for clean-non-alpha flag early
    clean_non_alphanumeric_flag = "--clean-non-alpha" in args
    if clean_non_alphanumeric_flag:
        args.remove("--clean-non-alpha")

    ####################
    # Process arguments
    ####################

    # Check for help request
    if "--help" in args or "-h" in args:
        print_usage_help()
        sys.exit(0)

    # Check for example code request
    elif "--example" in args:
        print_example_code()
        sys.exit(0)

    # Check for demo request
    elif "--demo" in args:
        run_live_demo(preserve_case=preserve_case)
        sys.exit(0)

    # Check for word processing
    elif "--word" in args:
        # Find the position of --word flag
        word_index = args.index("--word")

        # Get all arguments after --word
        words_to_stem = args[word_index + 1 :]

        # Check if any words were provided
        if not words_to_stem:
            print("Error: No words provided after --word flag")
            print("Example: python porter_stemmer.py --word running flies")
            sys.exit(1)

        # Process the words with case preference
        stem_words_from_args(words_to_stem, preserve_case=preserve_case)
        sys.exit(0)

    # Check for file processing
    elif "--file" in args:
        # Find the position of --file flag
        file_index = args.index("--file")

        # Check if filename was provided
        if file_index + 1 >= len(args):
            print("Error: No filename provided after --file flag")
            print("Example: python porter_stemmer.py --file document.txt")
            sys.exit(1)

        # Get the filename
        filename = args[file_index + 1]

        # Create instance WITH the preserve_case setting
        stemmer_instance = PorterVanillaPyStemmer(to_lowercase=not preserve_case)

        """
        def stem_file_wrapper(
            self, 
            filename, 
            preserve_case=False, 
            output_file=None, 
            show_progress=False
        )
        """
        # Process the file (no need to pass preserve_case again)
        stemmer_instance.stem_file_wrapper(
            filename,
            preserve_case=False,
            output_file="converted.txt",
            clean_non_alphanumeric=clean_non_alphanumeric_flag,
        )
        sys.exit(0)

    # # Simple Version
    # elif '--file' in args:
    #     file_index = args.index('--file')
    #     if file_index + 1 >= len(args):
    #         print("Error: No filename provided")
    #         sys.exit(1)

    #     filename = args[file_index + 1]

    #     # Create stemmer and process file
    #     stemmer = PorterVanillaPyStemmer(to_lowercase=not preserve_case)
    #     stemmer.stem_file_simple(filename, "output.txt")
    #     print(f"Done. Output written to output.txt")

    # Check for test request
    elif "--test" in args:
        # Run comprehensive tests
        print()
        success = run_comprehensive_tests()

        if success:
            print("\n✓ All tests passed!")
            sys.exit(0)
        else:
            print("\n✗ Some tests failed!")
            sys.exit(1)

    # Unknown argument
    else:
        print(f"Error: Unknown argument '{args[0]}'")
        print("Use --help to see available options")
        sys.exit(1)
