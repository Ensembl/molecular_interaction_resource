from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q

from rest_framework.mixins import (
    CreateModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin
)
from rest_framework.viewsets import GenericViewSet
import home.models as DBtables
from .models import Species, EnsemblGene
from home.serializers import SpeciesSerializer, InteractionSerializer, EnsemblGeneSerializer
from django.core.serializers import serialize
from .serializers import LazyEncoder
import json
from json import JSONEncoder
import numpy as np

# Create your views here.
def index(request):
    return HttpResponse("Welcome! You're at the MolIntXS index.")

def prediction_method(request):
    return HttpResponse("Welcome! You're at the prediction_method response page.")

def species_id(request, species_id):
    species_list = DBtables.Species.objects.filter(species_id=species_id)
    json_species = serialize('jsonl', species_list, cls=LazyEncoder)  

    return HttpResponse(json_species)

def species(request):
    species_list = DBtables.Species.objects.all()
    json_species = serialize('jsonl', species_list, cls=LazyEncoder) 
    
    return HttpResponse(json_species)

def ensembl_gene(request):
    gene_list = DBtables.EnsemblGene.objects.all()
    json_genes = serialize('jsonl', gene_list, cls=LazyEncoder) 
    
    return HttpResponse(json_genes)

def interactions_by_prodname(request):
    species = DBtables.Species.objects.all()
    species_genes_List = []
    species_dict = {}
    for sp in species:
        sp_id = sp.species_id
        genes = DBtables.EnsemblGene.objects.filter(Q(curatedinteractor__interaction_for_int2__interactor_2__ensembl_gene__species_id=sp_id) | Q(curatedinteractor__interaction_for_int1__interactor_1__ensembl_gene__species_id=sp_id))
        genes_per_specie_List = []
        for gene in genes:
            if 'UNDETERMINED' not in gene.ensembl_stable_id:
                genes_per_specie_List.append(gene.ensembl_stable_id)
        if genes_per_specie_List:
            unique_gene_list = list(set(genes_per_specie_List))
            species_dict = {sp.production_name:unique_gene_list}
            species_genes_List.append(species_dict)
    json_species_genes_list = json.loads(str(species_genes_List).replace("'",'"'))
    return HttpResponse(json_species_genes_list)
        
def display_by_gene(request,ens_stbl_id):
    InteractionsByGene = DBtables.Interaction.objects.filter(Q(interactor_1__ensembl_gene_id__ensembl_stable_id__contains=ens_stbl_id) | Q(interactor_2__ensembl_gene_id__ensembl_stable_id__contains=ens_stbl_id))
    InteractionsByGeneList = []
    for intrctn in InteractionsByGene:
        interactor1_type = intrctn.interactor_1.interactor_type
        species1_name = intrctn.interactor_1.ensembl_gene.species.production_name 
        identifier1 = intrctn.interactor_1.curies
        ens_stbl_id_1 = intrctn.interactor_1.ensembl_gene.ensembl_stable_id
        
        interactor1_dict = {"type":"species","name": species1_name,"gene": ens_stbl_id_1,"interactor":interactor1_type,"identifier": identifier1}
        
        interactor2_type = intrctn.interactor_2.interactor_type
        identifier2 = intrctn.interactor_2.curies
        source_db = intrctn.source_db.label
        if interactor2_type == 'synthetic':
            interactor2_name = intrctn.interactor_2.name
            interactor2_dict = {"type":"other", "name": interactor2_name,"interactor": interactor2_type,"identifier":identifier2,"source_DB": source_db}
        else:
            species2_name = intrctn.interactor_2.ensembl_gene.species.production_name 
            ens_stbl_id_2 = intrctn.interactor_2.ensembl_gene.ensembl_stable_id
            interactor2_dict = {"type":"species", "name": species2_name,"gene": ens_stbl_id_2,"interactor":interactor2_type,"identifier": identifier2,"source_DB": source_db}
        
        MetadataByInteraction = DBtables.KeyValuePair.objects.filter(interaction_id=intrctn.interaction_id)
        metadataList = []
        
        for mo in MetadataByInteraction:
            metadata_dict = {}
            metadata_dict["label"] = mo.meta_key.name
            metadata_dict["value"] = mo.value
            metadataList.append(metadata_dict)

        interactionDict = {"interactor_1":interactor1_dict, "interactor_2":interactor2_dict, "metadata":metadataList}
        
        InteractionsByGeneList.append(interactionDict)
        
    json_interactions_by_gene_list = json.dumps(InteractionsByGeneList)
    return HttpResponse(json_interactions_by_gene_list)

class InteractionsForEnsgeneProdnameViewSet(
    GenericViewSet,  # generic view functionality
    RetrieveModelMixin,  # handles GETs for 1 Species
    ListModelMixin):  # handles GETs for many Species

    serializer_class = InteractionSerializer

    def get_queryset(self):
        ens_gene = self.kwargs['ens_gene']
        prod_name = self.kwargs['prod_name']
        return DBtables.Interaction.objects.filter(Q(interactor_1__ensembl_gene_id__ensembl_stable_id__contains=ens_gene) | Q(interactor_2__ensembl_gene_id__ensembl_stable_id__contains=ens_gene)).filter(Q(interactor_1__ensembl_gene_id__species_id__production_name__contains=prod_name) | Q(interactor_2__ensembl_gene_id__species_id__production_name__contains=prod_name))

def source_db(request):
    return HttpResponse("Welcome! You're at the source_db response page.")

def meta_key(request):
    return HttpResponse("Welcome! You're at the meta_key response page.")

def ontology(request):
    return HttpResponse("Welcome! You're at the ontology response page.")

def ontology_term(request):
    return HttpResponse("Welcome! You're at the ontology_term response page.")

def curated_interactor(request):
    return HttpResponse("Welcome! You're at the curated_interactor response page.")

def predicted_interactor(request):
    return HttpResponse("Welcome! You're at the predicted_interactor response page.")

def interaction(request):
    return HttpResponse("Welcome! You're at the interaction response page.")

def key_value_pair(request):
    return HttpResponse("Welcome! You're at the key_value_pair response page.")

class SpeciesViewSet(GenericViewSet,  # generic view functionality
                     CreateModelMixin,  # handles POSTs
                     RetrieveModelMixin,  # handles GETs for 1 Species
                     UpdateModelMixin,  # handles PUTs and PATCHes
                     ListModelMixin):  # handles GETs for many Species

      serializer_class = SpeciesSerializer
      queryset = DBtables.Species.objects.all()

class EnsemblGeneViewSet(GenericViewSet,  # generic view functionality
                     CreateModelMixin,  # handles POSTs
                     RetrieveModelMixin,  # handles GETs for 1 EnsemblGene
                     UpdateModelMixin,  # handles PUTs and PATCHes
                     ListModelMixin):  # handles GETs for many EnsemblGene

      serializer_class = EnsemblGeneSerializer
      queryset = DBtables.EnsemblGene.objects.all()

