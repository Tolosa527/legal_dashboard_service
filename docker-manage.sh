#!/bin/bash

# Legal Dashboard Docker Management Script

set -e

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
        
        echo ""
        echo "✅ Legal Dashboard is ready!"
        echo ""
        echo "📋 Service URLs:"
        echo "   🗄️  MongoDB: mongodb://admin:adminpassword@localhost:27017"
        echo "   🌐 Mongo Express: http://localhost:8081 (admin/express123)"
        echo ""
        echo "📈 To view logs: ./docker-manage.sh logs"
        echo "🛑 To stop: ./docker-manage.sh stop"
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
        $DOCKER_COMPOSE up data-sync
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
        echo "Usage: $0 {start|stop|restart|sync|logs|status|clean|shell-mongo}"
        echo ""
        echo "Commands:"
        echo "  start        - Start all services and sync data"
        echo "  stop         - Stop all services"
        echo "  restart      - Restart all services"
        echo "  sync         - Re-sync police data from external PostgreSQL to MongoDB"
        echo "  logs [service] - View logs (optionally for specific service)"
        echo "  status       - Show service status"
        echo "  clean        - Remove containers and volumes"
        echo "  shell-mongo  - Open MongoDB shell"
        exit 1
        ;;
esac
