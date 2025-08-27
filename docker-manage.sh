#!/bin/bash

# Legal Dashboard Docker Management Script

set -e

# Change to deployment directory
cd "$(dirname "$0")/deployment"

# Use docker compose (new) instead of docker-compose (old)
DOCKER_COMPOSE="docker compose"

echo "🚀 Legal Dashboard Docker Management"
echo "===================================="

case "$1" in
    "start")
        echo "🔄 Starting Legal Dashboard services..."
        $DOCKER_COMPOSE up -d mongodb mongo-express
        
        echo "⏳ Waiting for databases to initialize..."
        sleep 10
        
        echo "📊 Running data synchronization..."
        $DOCKER_COMPOSE up data-sync
        
        echo " Starting Reflex application..."
        $DOCKER_COMPOSE up -d reflex-app
        
        echo ""
        echo "✅ Legal Dashboard is ready!"
        echo ""
        echo "📋 Service URLs:"
        echo "   🗄️  MongoDB: mongodb://admin:adminpassword@localhost:27017"
        echo "   🌐 Mongo Express: http://localhost:8081 (admin/express123)"
        echo "   📊 Reflex App: http://localhost:3000"
        echo "   🔌 API Backend: http://localhost:8000"
        echo ""
        echo "📈 To view logs: ./docker-manage.sh logs"
        echo "🛑 To stop: ./docker-manage.sh stop"
        ;;

    "demo")
        echo "🔄 Starting Legal Dashboard with Reflex app (same as start)..."
        $0 start
        ;;

    "reflex-start")
        echo "🚀 Starting only Reflex application..."
        $DOCKER_COMPOSE up -d reflex-app
        echo "✅ Reflex app is running at http://localhost:3000"
        ;;

    "reflex-stop")
        echo "🛑 Stopping Reflex application..."
        $DOCKER_COMPOSE stop reflex-app
        echo "✅ Reflex app stopped"
        ;;

    "reflex-restart")
        echo "🔄 Restarting Reflex application..."
        $DOCKER_COMPOSE restart reflex-app
        echo "✅ Reflex app restarted"
        ;;

    "reflex-rebuild")
        echo "🔨 Rebuilding and starting Reflex application..."
        $DOCKER_COMPOSE stop reflex-app
        $DOCKER_COMPOSE build --no-cache reflex-app
        $DOCKER_COMPOSE up -d reflex-app
        echo "✅ Reflex app rebuilt and started at http://localhost:3000"
        ;;

    "reflex-logs")
        echo "📋 Viewing Reflex application logs..."
        $DOCKER_COMPOSE logs -f reflex-app
        ;;
        
    "stop")
        echo "🛑 Stopping Legal Dashboard services..."
        $DOCKER_COMPOSE down
        echo "✅ All services stopped"
        ;;
        
    "restart")
        echo "🔄 Restarting Legal Dashboard services..."
        $0 stop
        sleep 2
        $0 start
        ;;
        
    "sync")
        echo "🔄 Re-syncing police data..."
        # Pass environment variables to the sync container
        if [ -n "${CLEAR_EXISTING:-}" ]; then
            $DOCKER_COMPOSE run --rm -e CLEAR_EXISTING="$CLEAR_EXISTING" data-sync
        else
            $DOCKER_COMPOSE up data-sync
        fi
        echo "✅ Data sync completed"
        ;;
        
    "logs")
        echo "📋 Viewing service logs..."
        $DOCKER_COMPOSE logs -f "${2:-}"
        ;;
        
    "status")
        echo "📊 Service Status:"
        $DOCKER_COMPOSE ps
        ;;
        
    "clean")
        echo "🧹 Cleaning up containers and volumes..."
        $DOCKER_COMPOSE down -v
        docker system prune -f
        echo "✅ Cleanup completed"
        ;;
        
    "shell-mongo")
        echo "🐚 Opening MongoDB shell..."
        $DOCKER_COMPOSE exec mongodb mongosh -u admin -p adminpassword legal_dashboard
        ;;
        
    *)
        echo "Usage: $0 {start|stop|restart|demo|sync|logs|status|clean|shell-mongo|reflex-start|reflex-stop|reflex-restart|reflex-rebuild|reflex-logs}"
        echo ""
        echo "Main Commands:"
        echo "  start        - Start all services and sync data"
        echo "  stop         - Stop all services"
        echo "  restart      - Restart all services"
        echo "  demo         - Start all services including Reflex app"
        echo "  sync         - Re-sync police data from external PostgreSQL to MongoDB"
        echo "  logs [service] - View logs (optionally for specific service)"
        echo "  status       - Show service status"
        echo "  clean        - Remove containers and volumes"
        echo "  shell-mongo  - Open MongoDB shell"
        echo ""
        echo "Reflex App Commands:"
        echo "  reflex-start   - Start only the Reflex application"
        echo "  reflex-stop    - Stop only the Reflex application"
        echo "  reflex-restart - Restart the Reflex application"
        echo "  reflex-rebuild - Rebuild and start the Reflex application"
        echo "  reflex-logs    - View Reflex application logs"
        exit 1
        ;;
esac
