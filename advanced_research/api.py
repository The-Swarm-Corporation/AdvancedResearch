"""
Advanced Research API Module

This module provides FastAPI-based REST API endpoints for the Advanced Research system.
It allows users to interact with the research system through HTTP requests.
"""

from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from loguru import logger
import uvicorn


class ResearchRequest(BaseModel):
    """Request model for research tasks."""

    task: str = Field(
        ..., description="The research question or task to execute"
    )
    img: Optional[str] = Field(
        None, description="Optional image input (base64 or URL)"
    )
    export_on: bool = Field(
        False, description="Whether to export results to JSON file"
    )
    output_type: str = Field(
        "final", description="Output format type"
    )


class ResearchResponse(BaseModel):
    """Response model for research results."""

    id: str = Field(
        ..., description="Unique identifier for the research session"
    )
    task: str = Field(..., description="The original research task")
    result: str = Field(..., description="The research findings")
    timestamp: str = Field(
        ..., description="Timestamp of the research completion"
    )
    exported_file: Optional[str] = Field(
        None, description="Path to exported JSON file if applicable"
    )


class BatchResearchRequest(BaseModel):
    """Request model for batch research tasks."""

    tasks: List[str] = Field(
        ...,
        description="List of research questions or tasks to execute",
    )
    export_on: bool = Field(
        False, description="Whether to export results to JSON files"
    )
    output_type: str = Field(
        "final", description="Output format type"
    )


class BatchResearchResponse(BaseModel):
    """Response model for batch research results."""

    batch_id: str = Field(
        ..., description="Unique identifier for the batch"
    )
    results: List[ResearchResponse] = Field(
        ..., description="List of research results"
    )
    total_tasks: int = Field(
        ..., description="Total number of tasks processed"
    )
    timestamp: str = Field(
        ..., description="Timestamp of the batch completion"
    )


class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str = Field(..., description="API status")
    timestamp: str = Field(..., description="Current timestamp")
    version: str = Field(..., description="API version")


def create_research_api(research_system) -> FastAPI:
    """
    Create and configure the FastAPI application for the Advanced Research system.

    Args:
        research_system: An instance of the AdvancedResearch class

    Returns:
        FastAPI: Configured FastAPI application
    """
    app = FastAPI(
        title="Advanced Research API",
        description="REST API for the Advanced Research multi-agent system",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure this properly for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/", response_model=HealthResponse)
    async def root():
        """Root endpoint with basic API information."""
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now().isoformat(),
            version="1.0.0",
        )

    @app.get("/health", response_model=HealthResponse)
    async def health_check():
        """Health check endpoint."""
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now().isoformat(),
            version="1.0.0",
        )

    @app.post("/research", response_model=ResearchResponse)
    async def conduct_research(request: ResearchRequest):
        """
        Conduct a single research task.

        Args:
            request: ResearchRequest containing the task and options

        Returns:
            ResearchResponse: The research results
        """
        try:
            logger.info(
                f"Starting research task: {request.task[:100]}..."
            )

            # Create a new research system instance for this request
            from advanced_research.main import (
                AdvancedResearch,
                generate_id,
            )

            research_id = generate_id()
            research_instance = AdvancedResearch(
                id=research_id,
                name=research_system.name,
                description=research_system.description,
                worker_model_name=research_system.worker_model_name,
                director_agent_name=research_system.director_agent_name,
                director_model_name=research_system.director_model_name,
                director_max_tokens=research_system.director_max_tokens,
                output_type=request.output_type,
                max_loops=research_system.max_loops,
                export_on=request.export_on,
                director_max_loops=research_system.director_max_loops,
                chat_interface=False,  # Always False for API
            )

            # Run the research
            result = research_instance.run(
                task=request.task, img=request.img
            )

            # Prepare response
            exported_file = (
                f"{research_id}.json" if request.export_on else None
            )

            return ResearchResponse(
                id=research_id,
                task=request.task,
                result=(
                    result
                    if result
                    else "Research completed successfully"
                ),
                timestamp=datetime.now().isoformat(),
                exported_file=exported_file,
            )

        except Exception as e:
            logger.error(f"Error in research task: {e}")
            raise HTTPException(
                status_code=500, detail=f"Research failed: {str(e)}"
            )

    @app.post("/research/batch", response_model=BatchResearchResponse)
    async def conduct_batch_research(request: BatchResearchRequest):
        """
        Conduct multiple research tasks in batch.

        Args:
            request: BatchResearchRequest containing the tasks and options

        Returns:
            BatchResearchResponse: The batch research results
        """
        try:
            logger.info(
                f"Starting batch research with {len(request.tasks)} tasks..."
            )

            from advanced_research.main import (
                AdvancedResearch,
                generate_id,
            )

            batch_id = generate_id()
            results = []

            for i, task in enumerate(request.tasks):
                logger.info(
                    f"Processing task {i+1}/{len(request.tasks)}: {task[:50]}..."
                )

                research_id = generate_id()
                research_instance = AdvancedResearch(
                    id=research_id,
                    name=research_system.name,
                    description=research_system.description,
                    worker_model_name=research_system.worker_model_name,
                    director_agent_name=research_system.director_agent_name,
                    director_model_name=research_system.director_model_name,
                    director_max_tokens=research_system.director_max_tokens,
                    output_type=request.output_type,
                    max_loops=research_system.max_loops,
                    export_on=request.export_on,
                    director_max_loops=research_system.director_max_loops,
                    chat_interface=False,
                )

                # Run the research
                result = research_instance.run(task=task)

                # Add to results
                exported_file = (
                    f"{research_id}.json"
                    if request.export_on
                    else None
                )
                results.append(
                    ResearchResponse(
                        id=research_id,
                        task=task,
                        result=(
                            result
                            if result
                            else "Research completed successfully"
                        ),
                        timestamp=datetime.now().isoformat(),
                        exported_file=exported_file,
                    )
                )

            return BatchResearchResponse(
                batch_id=batch_id,
                results=results,
                total_tasks=len(request.tasks),
                timestamp=datetime.now().isoformat(),
            )

        except Exception as e:
            logger.error(f"Error in batch research: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Batch research failed: {str(e)}",
            )

    @app.get("/research/methods")
    async def get_output_methods():
        """Get available output formatting methods."""
        try:
            methods = research_system.get_output_methods()
            return {"output_methods": methods}
        except Exception as e:
            logger.error(f"Error getting output methods: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get output methods: {str(e)}",
            )

    @app.get("/system/info")
    async def get_system_info():
        """Get information about the research system configuration."""
        return {
            "name": research_system.name,
            "description": research_system.description,
            "director_agent_name": research_system.director_agent_name,
            "director_model_name": research_system.director_model_name,
            "director_max_tokens": research_system.director_max_tokens,
            "max_loops": research_system.max_loops,
            "director_max_loops": research_system.director_max_loops,
        }

    return app


def run_api_server(
    research_system,
    host: str = "127.0.0.1",
    port: int = 8000,
    reload: bool = False,
    **kwargs,
):
    """
    Run the FastAPI server for the Advanced Research API.

    Args:
        research_system: An instance of the AdvancedResearch class
        host: Server host address
        port: Server port
        reload: Enable auto-reload for development
        **kwargs: Additional arguments to pass to uvicorn.run()
    """
    app = create_research_api(research_system)

    logger.info("Starting Advanced Research API server...")
    logger.info(f"API Documentation: http://{host}:{port}/docs")
    logger.info(f"ReDoc Documentation: http://{host}:{port}/redoc")
    logger.info(f"Health Check: http://{host}:{port}/health")

    uvicorn.run(
        app,
        host=host,
        port=port,
        # reload=reload,
        workers=1,
        **kwargs,
    )
