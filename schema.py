import graphene


class Query(graphene.ObjectType):
    hello = graphene.String()
    greeting = graphene.String(name=graphene.String(default_value="world"))

    def resolve_hello(self, info):
        return "hello Bello"

    def resolve_greeting(self, info, name):
        return f"Hello {name}"

schema = graphene.Schema(query=Query)