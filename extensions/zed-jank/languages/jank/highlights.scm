(sym_lit) @variable
(num_lit) @number
[(str_lit) (char_lit)] @string
(regex_lit) @string.regex
(bool_lit) @boolean
(nil_lit) @constant.builtin
(kwd_lit) @constant

["(" ")" "[" "]" "{" "}"] @punctuation.bracket
["'" "`" "~" "~@" "@" "#'" "#" "#?" "#?@"] @operator

(list_lit . (sym_lit) @function)

(list_lit
  . (sym_lit) @keyword
  (#any-of? @keyword
    "ns" "in-ns" "def" "defonce" "defn" "defn-" "defmacro"
    "do" "if" "if-not" "if-let" "when" "when-not" "when-let"
    "let" "let*" "letfn" "fn" "fn*" "loop" "loop*" "recur"
    "quote" "var" "throw" "try" "catch" "finally" "set!"
    "binding" "cond" "case" "and" "or" "doseq" "for" "->" "->>"))

; Native symbols are useful in value position as well as function calls.
((sym_lit namespace: (sym_ns) @_namespace) @function
  (#eq? @_namespace "cpp"))

(tagged_or_ctor_lit
  tag: (sym_lit) @type
  (#eq? @type "cpp"))

(comment) @comment
(dis_expr) @comment
