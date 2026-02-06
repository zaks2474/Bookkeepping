time="2026-02-06T14:47:22-06:00" level=warning msg="/home/zaks/zakops-agent-api/apps/agent-api/docker-compose.yml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion"
time="2026-02-06T14:47:22-06:00" level=warning msg="The \"OPENAI_API_KEY\" variable is not set. Defaulting to a blank string."
--
-- PostgreSQL database dump
--

\restrict EzhbZZsRRTnGeIy7WdXh9YdZeb3RYnQgfHboCopaqGr3KpZMCpL2YMsl9hna49b

-- Dumped from database version 16.11 (Debian 16.11-1.pgdg12+1)
-- Dumped by pg_dump version 16.11 (Debian 16.11-1.pgdg12+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- Name: cleanup_expired_approvals(); Type: FUNCTION; Schema: public; Owner: agent
--

CREATE FUNCTION public.cleanup_expired_approvals() RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    expired_count INTEGER;
BEGIN
    UPDATE approvals
    SET status = 'expired'
    WHERE status = 'pending'
      AND expires_at IS NOT NULL
      AND expires_at < NOW();

    GET DIAGNOSTICS expired_count = ROW_COUNT;
    RETURN expired_count;
END;
$$;


ALTER FUNCTION public.cleanup_expired_approvals() OWNER TO agent;

--
-- Name: prevent_audit_log_delete(); Type: FUNCTION; Schema: public; Owner: agent
--

CREATE FUNCTION public.prevent_audit_log_delete() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
  RAISE EXCEPTION 'DELETE on audit_log is prohibited — append-only table (chain-of-custody)';
  RETURN NULL;
END;
$$;


ALTER FUNCTION public.prevent_audit_log_delete() OWNER TO agent;

--
-- Name: reclaim_stale_claims(integer); Type: FUNCTION; Schema: public; Owner: agent
--

CREATE FUNCTION public.reclaim_stale_claims(stale_threshold_minutes integer DEFAULT 5) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    reclaimed_count INTEGER;
BEGIN
    UPDATE approvals
    SET status = 'pending',
        claimed_at = NULL
    WHERE status = 'claimed'
      AND claimed_at < NOW() - (stale_threshold_minutes || ' minutes')::INTERVAL;

    GET DIAGNOSTICS reclaimed_count = ROW_COUNT;
    RETURN reclaimed_count;
END;
$$;


ALTER FUNCTION public.reclaim_stale_claims(stale_threshold_minutes integer) OWNER TO agent;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: approvals; Type: TABLE; Schema: public; Owner: agent
--

CREATE TABLE public.approvals (
    id character varying(36) DEFAULT (public.uuid_generate_v4())::text NOT NULL,
    thread_id character varying(255) NOT NULL,
    checkpoint_id character varying(255),
    tool_name character varying(255) NOT NULL,
    tool_args text NOT NULL,
    actor_id character varying(255) NOT NULL,
    status character varying(20) DEFAULT 'pending'::character varying NOT NULL,
    idempotency_key character varying(255) NOT NULL,
    claimed_at timestamp with time zone,
    resolved_at timestamp with time zone,
    resolved_by character varying(255),
    rejection_reason text,
    expires_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    CONSTRAINT approvals_status_check CHECK (((status)::text = ANY ((ARRAY['pending'::character varying, 'claimed'::character varying, 'approved'::character varying, 'rejected'::character varying, 'expired'::character varying])::text[])))
);


ALTER TABLE public.approvals OWNER TO agent;

--
-- Name: TABLE approvals; Type: COMMENT; Schema: public; Owner: agent
--

COMMENT ON TABLE public.approvals IS 'HITL approval requests for tool executions requiring human review';


--
-- Name: audit_log; Type: TABLE; Schema: public; Owner: agent
--

CREATE TABLE public.audit_log (
    id character varying(36) DEFAULT (public.uuid_generate_v4())::text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    actor_id character varying(255) NOT NULL,
    event_type character varying(100) NOT NULL,
    thread_id character varying(255),
    approval_id character varying(36),
    tool_execution_id character varying(36),
    payload jsonb DEFAULT '{}'::jsonb NOT NULL,
    CONSTRAINT audit_log_event_type_check CHECK (((event_type)::text = ANY ((ARRAY['approval_created'::character varying, 'approval_claimed'::character varying, 'approval_approved'::character varying, 'approval_rejected'::character varying, 'approval_expired'::character varying, 'tool_execution_started'::character varying, 'tool_execution_completed'::character varying, 'tool_execution_failed'::character varying, 'stale_claim_reclaimed'::character varying])::text[])))
);


ALTER TABLE public.audit_log OWNER TO agent;

--
-- Name: TABLE audit_log; Type: COMMENT; Schema: public; Owner: agent
--

COMMENT ON TABLE public.audit_log IS 'Immutable audit trail for all approval and execution events';


--
-- Name: audit_log_archive; Type: TABLE; Schema: public; Owner: agent
--

CREATE TABLE public.audit_log_archive (
    id character varying(36) DEFAULT (public.uuid_generate_v4())::text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    actor_id character varying(255) NOT NULL,
    event_type character varying(100) NOT NULL,
    thread_id character varying(255),
    approval_id character varying(36),
    tool_execution_id character varying(36),
    payload jsonb DEFAULT '{}'::jsonb NOT NULL,
    CONSTRAINT audit_log_event_type_check CHECK (((event_type)::text = ANY ((ARRAY['approval_created'::character varying, 'approval_claimed'::character varying, 'approval_approved'::character varying, 'approval_rejected'::character varying, 'approval_expired'::character varying, 'tool_execution_started'::character varying, 'tool_execution_completed'::character varying, 'tool_execution_failed'::character varying, 'stale_claim_reclaimed'::character varying])::text[])))
);


ALTER TABLE public.audit_log_archive OWNER TO agent;

--
-- Name: checkpoint_blobs; Type: TABLE; Schema: public; Owner: agent
--

CREATE TABLE public.checkpoint_blobs (
    thread_id text NOT NULL,
    checkpoint_ns text DEFAULT ''::text NOT NULL,
    channel text NOT NULL,
    version text NOT NULL,
    type text NOT NULL,
    blob bytea
);


ALTER TABLE public.checkpoint_blobs OWNER TO agent;

--
-- Name: checkpoint_migrations; Type: TABLE; Schema: public; Owner: agent
--

CREATE TABLE public.checkpoint_migrations (
    v integer NOT NULL
);


ALTER TABLE public.checkpoint_migrations OWNER TO agent;

--
-- Name: checkpoint_writes; Type: TABLE; Schema: public; Owner: agent
--

CREATE TABLE public.checkpoint_writes (
    thread_id text NOT NULL,
    checkpoint_ns text DEFAULT ''::text NOT NULL,
    checkpoint_id text NOT NULL,
    task_id text NOT NULL,
    idx integer NOT NULL,
    channel text NOT NULL,
    type text,
    blob bytea NOT NULL,
    task_path text DEFAULT ''::text NOT NULL
);


ALTER TABLE public.checkpoint_writes OWNER TO agent;

--
-- Name: checkpoints; Type: TABLE; Schema: public; Owner: agent
--

CREATE TABLE public.checkpoints (
    thread_id text NOT NULL,
    checkpoint_ns text DEFAULT ''::text NOT NULL,
    checkpoint_id text NOT NULL,
    parent_checkpoint_id text,
    type text,
    checkpoint jsonb NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb NOT NULL
);


ALTER TABLE public.checkpoints OWNER TO agent;

--
-- Name: decision_ledger; Type: TABLE; Schema: public; Owner: agent
--

CREATE TABLE public.decision_ledger (
    id character varying(36) DEFAULT (public.uuid_generate_v4())::text NOT NULL,
    correlation_id character varying(255),
    thread_id character varying(255) NOT NULL,
    user_id character varying(255) NOT NULL,
    deal_id character varying(255),
    trigger_type character varying(50) NOT NULL,
    trigger_content text,
    prompt_version character varying(50),
    tools_considered text[],
    tool_selected character varying(255),
    selection_reason text,
    tool_name character varying(255),
    tool_args text,
    tool_result_preview text,
    hitl_required boolean DEFAULT false NOT NULL,
    approval_id character varying(36),
    approval_status character varying(20),
    success boolean DEFAULT true NOT NULL,
    error text,
    response_preview text,
    latency_ms integer,
    token_count integer,
    created_at timestamp with time zone DEFAULT now(),
    CONSTRAINT decision_ledger_trigger_type_check CHECK (((trigger_type)::text = ANY ((ARRAY['user_message'::character varying, 'tool_result'::character varying, 'system_prompt'::character varying, 'hitl_resume'::character varying])::text[])))
);


ALTER TABLE public.decision_ledger OWNER TO agent;

--
-- Name: TABLE decision_ledger; Type: COMMENT; Schema: public; Owner: agent
--

COMMENT ON TABLE public.decision_ledger IS 'R3 REMEDIATION [P2.6]: Agent reasoning and tool selection ledger for explainability';


--
-- Name: session; Type: TABLE; Schema: public; Owner: agent
--

CREATE TABLE public.session (
    created_at timestamp without time zone NOT NULL,
    id character varying NOT NULL,
    user_id integer NOT NULL,
    name character varying NOT NULL
);


ALTER TABLE public.session OWNER TO agent;

--
-- Name: tool_executions; Type: TABLE; Schema: public; Owner: agent
--

CREATE TABLE public.tool_executions (
    id character varying(36) DEFAULT (public.uuid_generate_v4())::text NOT NULL,
    approval_id character varying(36),
    idempotency_key character varying(255) NOT NULL,
    tool_name character varying(255) NOT NULL,
    tool_args text NOT NULL,
    status character varying(20) DEFAULT 'claimed'::character varying NOT NULL,
    result text,
    success boolean DEFAULT false NOT NULL,
    error_message text,
    claimed_at timestamp with time zone DEFAULT now() NOT NULL,
    executed_at timestamp with time zone,
    completed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    CONSTRAINT tool_executions_status_check CHECK (((status)::text = ANY ((ARRAY['claimed'::character varying, 'running'::character varying, 'succeeded'::character varying, 'failed'::character varying])::text[])))
);


ALTER TABLE public.tool_executions OWNER TO agent;

--
-- Name: TABLE tool_executions; Type: COMMENT; Schema: public; Owner: agent
--

COMMENT ON TABLE public.tool_executions IS 'Claim-first idempotent tool execution log';


--
-- Name: user; Type: TABLE; Schema: public; Owner: agent
--

CREATE TABLE public."user" (
    created_at timestamp without time zone NOT NULL,
    id integer NOT NULL,
    email character varying NOT NULL,
    hashed_password character varying NOT NULL
);


ALTER TABLE public."user" OWNER TO agent;

--
-- Name: user_id_seq; Type: SEQUENCE; Schema: public; Owner: agent
--

CREATE SEQUENCE public.user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_id_seq OWNER TO agent;

--
-- Name: user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: agent
--

ALTER SEQUENCE public.user_id_seq OWNED BY public."user".id;


--
-- Name: user id; Type: DEFAULT; Schema: public; Owner: agent
--

ALTER TABLE ONLY public."user" ALTER COLUMN id SET DEFAULT nextval('public.user_id_seq'::regclass);


--
-- Name: approvals approvals_idempotency_key_key; Type: CONSTRAINT; Schema: public; Owner: agent
--

ALTER TABLE ONLY public.approvals
    ADD CONSTRAINT approvals_idempotency_key_key UNIQUE (idempotency_key);


--
-- Name: approvals approvals_pkey; Type: CONSTRAINT; Schema: public; Owner: agent
--

ALTER TABLE ONLY public.approvals
    ADD CONSTRAINT approvals_pkey PRIMARY KEY (id);


--
-- Name: audit_log_archive audit_log_archive_pkey; Type: CONSTRAINT; Schema: public; Owner: agent
--

ALTER TABLE ONLY public.audit_log_archive
    ADD CONSTRAINT audit_log_archive_pkey PRIMARY KEY (id);


--
-- Name: audit_log audit_log_pkey; Type: CONSTRAINT; Schema: public; Owner: agent
--

ALTER TABLE ONLY public.audit_log
    ADD CONSTRAINT audit_log_pkey PRIMARY KEY (id);


--
-- Name: checkpoint_blobs checkpoint_blobs_pkey; Type: CONSTRAINT; Schema: public; Owner: agent
--

ALTER TABLE ONLY public.checkpoint_blobs
    ADD CONSTRAINT checkpoint_blobs_pkey PRIMARY KEY (thread_id, checkpoint_ns, channel, version);


--
-- Name: checkpoint_migrations checkpoint_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: agent
--

ALTER TABLE ONLY public.checkpoint_migrations
    ADD CONSTRAINT checkpoint_migrations_pkey PRIMARY KEY (v);


--
-- Name: checkpoint_writes checkpoint_writes_pkey; Type: CONSTRAINT; Schema: public; Owner: agent
--

ALTER TABLE ONLY public.checkpoint_writes
    ADD CONSTRAINT checkpoint_writes_pkey PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id, task_id, idx);


--
-- Name: checkpoints checkpoints_pkey; Type: CONSTRAINT; Schema: public; Owner: agent
--

ALTER TABLE ONLY public.checkpoints
    ADD CONSTRAINT checkpoints_pkey PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id);


--
-- Name: decision_ledger decision_ledger_pkey; Type: CONSTRAINT; Schema: public; Owner: agent
--

ALTER TABLE ONLY public.decision_ledger
    ADD CONSTRAINT decision_ledger_pkey PRIMARY KEY (id);


--
-- Name: session session_pkey; Type: CONSTRAINT; Schema: public; Owner: agent
--

ALTER TABLE ONLY public.session
    ADD CONSTRAINT session_pkey PRIMARY KEY (id);


--
-- Name: tool_executions tool_executions_idempotency_key_key; Type: CONSTRAINT; Schema: public; Owner: agent
--

ALTER TABLE ONLY public.tool_executions
    ADD CONSTRAINT tool_executions_idempotency_key_key UNIQUE (idempotency_key);


--
-- Name: tool_executions tool_executions_pkey; Type: CONSTRAINT; Schema: public; Owner: agent
--

ALTER TABLE ONLY public.tool_executions
    ADD CONSTRAINT tool_executions_pkey PRIMARY KEY (id);


--
-- Name: user user_pkey; Type: CONSTRAINT; Schema: public; Owner: agent
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


--
-- Name: audit_log_archive_actor_id_idx; Type: INDEX; Schema: public; Owner: agent
--

CREATE INDEX audit_log_archive_actor_id_idx ON public.audit_log_archive USING btree (actor_id);


--
-- Name: audit_log_archive_approval_id_idx; Type: INDEX; Schema: public; Owner: agent
--

CREATE INDEX audit_log_archive_approval_id_idx ON public.audit_log_archive USING btree (approval_id);


--
-- Name: audit_log_archive_created_at_idx; Type: INDEX; Schema: public; Owner: agent
--

CREATE INDEX audit_log_archive_created_at_idx ON public.audit_log_archive USING btree (created_at);


--
-- Name: audit_log_archive_event_type_idx; Type: INDEX; Schema: public; Owner: agent
--

CREATE INDEX audit_log_archive_event_type_idx ON public.audit_log_archive USING btree (event_type);


--
-- Name: audit_log_archive_thread_id_idx; Type: INDEX; Schema: public; Owner: agent
--

CREATE INDEX audit_log_archive_thread_id_idx ON public.audit_log_archive USING btree (thread_id);


--
-- Name: checkpoint_blobs_thread_id_idx; Type: INDEX; Schema: public; Owner: agent
--

CREATE INDEX checkpoint_blobs_thread_id_idx ON public.checkpoint_blobs USING btree (thread_id);


--
-- Name: checkpoint_writes_thread_id_idx; Type: INDEX; Schema: public; Owner: agent
--

CREATE INDEX checkpoint_writes_thread_id_idx ON public.checkpoint_writes USING btree (thread_id);


--
-- Name: checkpoints_thread_id_idx; Type: INDEX; Schema: public; Owner: agent
--

CREATE INDEX checkpoints_thread_id_idx ON public.checkpoints USING btree (thread_id);


--
-- Name: idx_approvals_actor_id; Type: INDEX; Schema: public; Owner: agent
--

CREATE INDEX idx_approvals_actor_id ON public.approvals USING btree (actor_id);


--
-- Name: idx_approvals_claimed_stale; Type: INDEX; Schema: public; Owner: agent
--

CREATE INDEX idx_approvals_claimed_stale ON public.approvals USING btree (claimed_at) WHERE ((status)::text = 'claimed'::text);


--
-- Name: idx_approvals_expires_at; Type: INDEX; Schema: public; Owner: agent
--

CREATE INDEX idx_approvals_expires_at ON public.approvals USING btree (expires_at) WHERE ((status)::text = 'pending'::text);


--
-- Name: idx_approvals_idempotency_key; Type: INDEX; Schema: public; Owner: agent
--

CREATE INDEX idx_approvals_idempotency_key ON public.approvals USING btree (idempotency_key);


--
-- Name: idx_approvals_status; Type: INDEX; Schema: public; Owner: agent
--

CREATE INDEX idx_approvals_status ON public.approvals USING btree (status);


--
-- Name: idx_approvals_thread_id; Type: INDEX; Schema: public; Owner: agent
--

CREATE INDEX idx_approvals_thread_id ON public.approvals USING btree (thread_id);


--
-- Name: idx_approvals_tool_name; Type: INDEX; Schema: public; Owner: agent
--

CREATE INDEX idx_approvals_tool_name ON public.approvals USING btree (tool_name);


--
-- Name: idx_audit_log_actor_id; Type: INDEX; Schema: public; Owner: agent
--

CREATE INDEX idx_audit_log_actor_id ON public.audit_log USING btree (actor_id);


--
-- Name: idx_audit_log_approval_id; Type: INDEX; Schema: public; Owner: agent
--

CREATE INDEX idx_audit_log_approval_id ON public.audit_log USING btree (approval_id);


--
-- Name: idx_audit_log_created_at; Type: INDEX; Schema: public; Owner: agent
--

CREATE INDEX idx_audit_log_created_at ON public.audit_log USING btree (created_at);


--
-- Name: idx_audit_log_event_type; Type: INDEX; Schema: public; Owner: agent
--

CREATE INDEX idx_audit_log_event_type ON public.audit_log USING btree (event_type);


--
-- Name: idx_audit_log_thread_id; Type: INDEX; Schema: public; Owner: agent
--

CREATE INDEX idx_audit_log_thread_id ON public.audit_log USING btree (thread_id);


--
-- Name: idx_decision_ledger_approval_id; Type: INDEX; Schema: public; Owner: agent
--

CREATE INDEX idx_decision_ledger_approval_id ON public.decision_ledger USING btree (approval_id);


--
-- Name: idx_decision_ledger_correlation_id; Type: INDEX; Schema: public; Owner: agent
--

CREATE INDEX idx_decision_ledger_correlation_id ON public.decision_ledger USING btree (correlation_id);


--
-- Name: idx_decision_ledger_created_at; Type: INDEX; Schema: public; Owner: agent
--

CREATE INDEX idx_decision_ledger_created_at ON public.decision_ledger USING btree (created_at);


--
-- Name: idx_decision_ledger_deal_id; Type: INDEX; Schema: public; Owner: agent
--

CREATE INDEX idx_decision_ledger_deal_id ON public.decision_ledger USING btree (deal_id);


--
-- Name: idx_decision_ledger_success; Type: INDEX; Schema: public; Owner: agent
--

CREATE INDEX idx_decision_ledger_success ON public.decision_ledger USING btree (success) WHERE (NOT success);


--
-- Name: idx_decision_ledger_thread_created; Type: INDEX; Schema: public; Owner: agent
--

CREATE INDEX idx_decision_ledger_thread_created ON public.decision_ledger USING btree (thread_id, created_at DESC);


--
-- Name: idx_decision_ledger_thread_id; Type: INDEX; Schema: public; Owner: agent
--

CREATE INDEX idx_decision_ledger_thread_id ON public.decision_ledger USING btree (thread_id);


--
-- Name: idx_decision_ledger_tool_name; Type: INDEX; Schema: public; Owner: agent
--

CREATE INDEX idx_decision_ledger_tool_name ON public.decision_ledger USING btree (tool_name);


--
-- Name: idx_decision_ledger_tool_selected; Type: INDEX; Schema: public; Owner: agent
--

CREATE INDEX idx_decision_ledger_tool_selected ON public.decision_ledger USING btree (tool_selected);


--
-- Name: idx_decision_ledger_user_id; Type: INDEX; Schema: public; Owner: agent
--

CREATE INDEX idx_decision_ledger_user_id ON public.decision_ledger USING btree (user_id);


--
-- Name: idx_tool_executions_approval_id; Type: INDEX; Schema: public; Owner: agent
--

CREATE INDEX idx_tool_executions_approval_id ON public.tool_executions USING btree (approval_id);


--
-- Name: idx_tool_executions_idempotency_key; Type: INDEX; Schema: public; Owner: agent
--

CREATE INDEX idx_tool_executions_idempotency_key ON public.tool_executions USING btree (idempotency_key);


--
-- Name: idx_tool_executions_success; Type: INDEX; Schema: public; Owner: agent
--

CREATE INDEX idx_tool_executions_success ON public.tool_executions USING btree (success);


--
-- Name: idx_tool_executions_tool_name; Type: INDEX; Schema: public; Owner: agent
--

CREATE INDEX idx_tool_executions_tool_name ON public.tool_executions USING btree (tool_name);


--
-- Name: ix_user_email; Type: INDEX; Schema: public; Owner: agent
--

CREATE UNIQUE INDEX ix_user_email ON public."user" USING btree (email);


--
-- Name: audit_log trg_prevent_audit_log_delete; Type: TRIGGER; Schema: public; Owner: agent
--

CREATE TRIGGER trg_prevent_audit_log_delete BEFORE DELETE ON public.audit_log FOR EACH ROW EXECUTE FUNCTION public.prevent_audit_log_delete();


--
-- Name: session session_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agent
--

ALTER TABLE ONLY public.session
    ADD CONSTRAINT session_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: tool_executions tool_executions_approval_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agent
--

ALTER TABLE ONLY public.tool_executions
    ADD CONSTRAINT tool_executions_approval_id_fkey FOREIGN KEY (approval_id) REFERENCES public.approvals(id) ON DELETE SET NULL;


--
-- PostgreSQL database dump complete
--

\unrestrict EzhbZZsRRTnGeIy7WdXh9YdZeb3RYnQgfHboCopaqGr3KpZMCpL2YMsl9hna49b

