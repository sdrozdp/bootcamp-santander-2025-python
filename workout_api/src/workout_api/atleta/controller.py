from datetime import datetime
from sqlalchemy.exc import IntegrityError
from uuid import uuid4
from fastapi import APIRouter, Body, HTTPException, status, Query
from pydantic import UUID4
from typing import List, Optional

from workout_api.atleta.schemas import AtletaIn, AtletaOut, AtletaUpdate, AtletaListOut
from workout_api.atleta.models import AtletaModel
from workout_api.categorias.models import CategoriaModel
from workout_api.centro_treinamento.models import CentroTreinamentoModel

from workout_api.contrib.dependencies import DatabaseDependency
from sqlalchemy.future import select

from fastapi_pagination import Page, paginate, Params
from fastapi.params import Depends 

router = APIRouter()

@router.post(
    '/', 
    summary='Criar um novo atleta',
    status_code=status.HTTP_201_CREATED,
    response_model=AtletaOut
)
async def post(
    db_session: DatabaseDependency, 
    atleta_in: AtletaIn = Body(...)
):
    categoria_nome = atleta_in.categoria.nome
    centro_treinamento_nome = atleta_in.centro_treinamento.nome

    categoria = (await db_session.execute(
        select(CategoriaModel).filter_by(nome=categoria_nome))
    ).scalars().first()
    
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f'A categoria {categoria_nome} não foi encontrada.'
        )
    
    centro_treinamento = (await db_session.execute(
        select(CentroTreinamentoModel).filter_by(nome=centro_treinamento_nome))
    ).scalars().first()
    
    if not centro_treinamento:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f'O centro de treinamento {centro_treinamento_nome} não foi encontrado.'
        )
    try:
        atleta_out = AtletaOut(id=uuid4(), created_at=datetime.utcnow(), **atleta_in.model_dump())
        atleta_model = AtletaModel(**atleta_out.model_dump(exclude={'categoria', 'centro_treinamento'}))

        atleta_model.categoria_id = categoria.pk_id
        atleta_model.centro_treinamento_id = centro_treinamento.pk_id
        
        db_session.add(atleta_model)
        await db_session.commit()

    except IntegrityError:
        await db_session.rollback()  # **Importante** para desfazer a transação
        raise HTTPException(
            status_code=303,
            detail=f"Já existe um atleta cadastrado com o cpf: {atleta_in.cpf}"
        )
    except Exception:
        await db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail='Ocorreu um erro ao inserir os dados no banco'
        )

    return atleta_out


# @router.get(
#     '/', 
#     summary='Consultar todos os Atletas',
#     status_code=status.HTTP_200_OK,
#     response_model=list[AtletaOut],
# )
# async def query(db_session: DatabaseDependency) -> list[AtletaOut]:
#     atletas: list[AtletaOut] = (await db_session.execute(select(AtletaModel))).scalars().all()
    
#     return [AtletaOut.model_validate(atleta) for atleta in atletas]

@router.get(
    '/',
    summary='Consultar todos os Atletas (nome, categoria e centro)',
    status_code=status.HTTP_200_OK,
    response_model=Page[AtletaListOut],  # <- aqui
)
async def query(db_session: DatabaseDependency, params: Params = Depends()) -> list[AtletaListOut]:
    result = await db_session.execute(
        select(
            AtletaModel.nome,
            CategoriaModel.nome.label('categoria'),
            CentroTreinamentoModel.nome.label('centro_treinamento')
        )
        .join(CategoriaModel, AtletaModel.categoria_id == CategoriaModel.pk_id)
        .join(CentroTreinamentoModel, AtletaModel.centro_treinamento_id == CentroTreinamentoModel.pk_id)
    )
    atletas_raw = result.all()

    atletas = [
        AtletaListOut.model_validate({
            "nome": atleta.nome,
            "categoria": atleta.categoria,
            "centro_treinamento": atleta.centro_treinamento
        })
        for atleta in atletas_raw
    ]
    return paginate(atletas, params)


@router.get(
    '/{id}', 
    summary='Consulta um Atleta pelo id',
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut,
)
async def get(id: UUID4, db_session: DatabaseDependency) -> AtletaOut:
    atleta: AtletaOut = (
        await db_session.execute(select(AtletaModel).filter_by(id=id))
    ).scalars().first()

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f'Atleta não encontrado no id: {id}'
        )
    
    return atleta


# rota por nome
@router.get(
    '/nome/{nome}',
    summary='Consulta atletas pelo nome',
    status_code=status.HTTP_200_OK,
    response_model=Page[AtletaOut],
)
async def get_atletas_by_nome(nome: str, db_session: DatabaseDependency, params: Params = Depends()) -> List[AtletaOut]:
    result = await db_session.execute(
        select(AtletaModel).filter(AtletaModel.nome.ilike(f"%{nome}%"))
    )
    atletas_raw = result.scalars().all()

    if not atletas_raw:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f'Nenhum atleta encontrado com nome: {nome}'
        )

    atletas = [AtletaOut.model_validate(c) for c in atletas_raw]

    return paginate(atletas, params)


# rota por cpf
@router.get(
    '/cpf/{cpf}',
    summary='Consulta atleta pelo cpf',
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut,
)
async def get_atleta_by_cpf(cpf: str, db_session: DatabaseDependency) -> AtletaOut:
    atleta = (
        await db_session.execute(select(AtletaModel).filter(AtletaModel.cpf == cpf))
    ).scalars().first()

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f'Atleta não encontrado com cpf: {cpf}'
        )

    return AtletaOut.model_validate(atleta)

@router.get(
    '/{id}', 
    summary='Consulta um Atleta pelo id',
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut,
)
async def get(id: UUID4, db_session: DatabaseDependency) -> AtletaOut:
    atleta: AtletaOut = (
        await db_session.execute(select(AtletaModel).filter_by(id=id))
    ).scalars().first()

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f'Atleta não encontrado no id: {id}'
        )
    
    return atleta

@router.patch(
    '/{id}', 
    summary='Editar um Atleta pelo id',
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut,
)
async def patch(id: UUID4, db_session: DatabaseDependency, atleta_up: AtletaUpdate = Body(...)) -> AtletaOut:
    atleta: AtletaOut = (
        await db_session.execute(select(AtletaModel).filter_by(id=id))
    ).scalars().first()

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f'Atleta não encontrado no id: {id}'
        )
    
    atleta_update = atleta_up.model_dump(exclude_unset=True)
    for key, value in atleta_update.items():
        setattr(atleta, key, value)

    await db_session.commit()
    await db_session.refresh(atleta)

    return atleta


@router.delete(
    '/{id}', 
    summary='Deletar um Atleta pelo id',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete(id: UUID4, db_session: DatabaseDependency) -> None:
    atleta: AtletaOut = (
        await db_session.execute(select(AtletaModel).filter_by(id=id))
    ).scalars().first()

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f'Atleta não encontrado no id: {id}'
        )
    
    await db_session.delete(atleta)
    await db_session.commit()