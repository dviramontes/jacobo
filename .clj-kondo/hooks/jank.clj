(ns hooks.jank
  (:require [clj-kondo.hooks-api :as api]))

(defn ns-form [{:keys [node]}]
  ;; Native headers are handled by jank. Preserve all other ns clauses so
  ;; clj-kondo still checks requires, aliases, and unknown options.
  {:node (with-meta
           (api/list-node
            (remove (fn [child]
                      (and (api/list-node? child)
                           (= :include (some-> child :children first api/sexpr))))
                    (:children node)))
           (meta node))})
