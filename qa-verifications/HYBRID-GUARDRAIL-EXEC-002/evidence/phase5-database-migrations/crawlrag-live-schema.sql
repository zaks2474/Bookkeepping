--
-- PostgreSQL database dump
--

\restrict JP0EwPLyz8YtLDdoWZAkYk2NjiL7kxuvq7kdjD4OCbFREPPWL6HUHY6caxz70pV

-- Dumped from database version 17.7 (Debian 17.7-3.pgdg12+1)
-- Dumped by pg_dump version 17.7 (Debian 17.7-3.pgdg12+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: vector; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public;


--
-- Name: EXTENSION vector; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION vector IS 'vector data type and ivfflat and hnsw access methods';


--
-- Name: match_crawledpage(public.vector, integer, jsonb); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.match_crawledpage(query_embedding public.vector, match_count integer DEFAULT 10, filter jsonb DEFAULT '{}'::jsonb) RETURNS TABLE(id bigint, url character varying, chunk_number integer, content text, metadata jsonb, similarity double precision)
    LANGUAGE plpgsql
    AS $$
#variable_conflict use_column
begin
  SET LOCAL ivfflat.probes = 10; -- Or a higher value if needed, e.g., 15 or 20
  return query
  select
    id::BIGINT,
    url,
    chunk_number,
    content,
    metadata,
    1 - (crawledpage.embedding <=> query_embedding) as similarity
  from crawledpage
  where metadata @> filter
  order by crawledpage.embedding <=> query_embedding
  limit match_count;
  -- Debug logging can be enabled here with:
  -- RAISE NOTICE 'Executed match_crawledpage with filter %', filter;
end;
$$;


ALTER FUNCTION public.match_crawledpage(query_embedding public.vector, match_count integer, filter jsonb) OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: crawledpage; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.crawledpage (
    id bigint NOT NULL,
    url character varying NOT NULL,
    chunk_number integer NOT NULL,
    content text NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb NOT NULL,
    embedding public.vector(1024),
    created_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL
);


ALTER TABLE public.crawledpage OWNER TO postgres;

--
-- Name: crawledpage_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.crawledpage_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.crawledpage_id_seq OWNER TO postgres;

--
-- Name: crawledpage_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.crawledpage_id_seq OWNED BY public.crawledpage.id;


--
-- Name: crawledpage id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crawledpage ALTER COLUMN id SET DEFAULT nextval('public.crawledpage_id_seq'::regclass);


--
-- Name: crawledpage crawledpage_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crawledpage
    ADD CONSTRAINT crawledpage_pkey PRIMARY KEY (id);


--
-- Name: crawledpage crawledpage_url_chunk_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crawledpage
    ADD CONSTRAINT crawledpage_url_chunk_number_key UNIQUE (url, chunk_number);


--
-- Name: crawledpage_embedding_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX crawledpage_embedding_idx ON public.crawledpage USING ivfflat (embedding public.vector_cosine_ops);


--
-- Name: idx_crawledpage_metadata; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_crawledpage_metadata ON public.crawledpage USING gin (metadata);


--
-- Name: idx_crawledpage_source; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_crawledpage_source ON public.crawledpage USING btree (((metadata ->> 'source'::text)));


--
-- Name: crawledpage Allow public read access; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY "Allow public read access" ON public.crawledpage FOR SELECT USING (true);


--
-- Name: crawledpage; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.crawledpage ENABLE ROW LEVEL SECURITY;

--
-- PostgreSQL database dump complete
--

\unrestrict JP0EwPLyz8YtLDdoWZAkYk2NjiL7kxuvq7kdjD4OCbFREPPWL6HUHY6caxz70pV

