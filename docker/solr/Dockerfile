FROM solr:6.6

ENV SOLR_CORE budgetportal

# Create Directories
RUN mkdir -p /opt/solr/server/solr/$SOLR_CORE/conf
RUN mkdir -p /opt/solr/server/solr/$SOLR_CORE/data

# Adding Files
ADD ./conf /opt/solr/server/solr/$SOLR_CORE/conf/
RUN cp -r /opt/solr/example/files/conf/lang /opt/solr/server/solr/$SOLR_CORE/conf/ && \
    cp -r /opt/solr/example/files/conf/stopwords.txt /opt/solr/server/solr/$SOLR_CORE/conf/ && \
    cp -r /opt/solr/example/files/conf/synonyms.txt /opt/solr/server/solr/$SOLR_CORE/conf/ && \
    cp -r /opt/solr/example/files/conf/protwords.txt /opt/solr/server/solr/$SOLR_CORE/conf/ && \
    cp -r /opt/solr/example/files/conf/currency.xml /opt/solr/server/solr/$SOLR_CORE/conf/ && \
    cp -r /opt/solr/example/files/conf/elevate.xml /opt/solr/server/solr/$SOLR_CORE/conf/

# Create Core.properties
RUN echo name=$SOLR_CORE > /opt/solr/server/solr/$SOLR_CORE/core.properties
