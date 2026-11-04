# Ontology

Material on modeling an ontology (knowledge graph) natively on Snowflake.

## Contents

* [Ontology on Snowflake - Explained](ontology-on-snowflake-explained.html) - A self-contained, visual HTML explainer (open it in a browser) covering:
  * **Nodes and edges** - how entities and relationships are stored as tables
  * **Time** - tracking how facts change over time
  * **Classes** - typing nodes and edges with an ontology class hierarchy
  * **Generated views** - views generated from the ontology metadata
  * **Five layers** - the layered architecture from raw data to consumption
  * **Routing** - how questions are routed to the right layer/object
  * **A question's journey** - an end-to-end walkthrough of answering a question
  * **Results through time** - point-in-time answers
  * **Paths** - traversing multi-hop relationships
  * **Putting it together** - summary of the full approach
* [Ontology on Snowflake for Retail & Consumer Goods - Explained](rcg-ontology-on-snowflake-explained.html) - The same explainer applied to a fictional RCG supply network: manufacturers and distributors (abstract **Supplier**), retailers (**Channel**) and promotions (**Event**), with `SUPPLIES` and `SERVES` unified into an abstract `sells_into` relation. It covers the same ten sections and follows the question *"Who was selling into FreshMart on 1 January 2025?"* from the agent down to `KG_EDGE`. All companies, dates and values are illustrative.
