(list_lit
  . (sym_lit) @context
  . (sym_lit name: (sym_name) @name)
  (#any-of? @context
    "ns" "def" "defonce" "defn" "defn-" "defmacro"
    "defmulti" "defmethod" "defprotocol" "defrecord" "deftype")) @item
