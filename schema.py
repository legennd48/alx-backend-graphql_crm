import graphene
from crm.schema import Query as CRMQuery, Mutation as CRMMutation


class Query(CRMQuery, graphene.ObjectType):
    hello = graphene.String()
    greeting = graphene.String(name=graphene.String(default_value="world"))

    def resolve_hello(self, info):
        return "hello Bello"

    def resolve_greeting(self, info, name):
        return f"Hello {name}"


class Mutation(CRMMutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)