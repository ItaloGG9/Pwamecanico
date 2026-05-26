from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, hash_password, create_access_token, get_current_user
from app.models.usuario import Taller, Usuario
from app.schemas.auth import LoginRequest, TokenResponse, RegisterRequest, UsuarioOut

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(Usuario).filter(Usuario.email == data.usuario.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    taller = Taller(**data.taller.model_dump())
    db.add(taller)
    db.flush()

    usuario = Usuario(
        taller_id=taller.id,
        nombre=data.usuario.nombre,
        email=data.usuario.email,
        password_hash=hash_password(data.usuario.password),
        rol="admin",
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    token = create_access_token({"sub": usuario.id, "taller_id": taller.id, "rol": usuario.rol})
    return TokenResponse(access_token=token, usuario=UsuarioOut.model_validate(usuario))


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == data.email).first()

    if not usuario or not verify_password(data.password, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
        )
    if not usuario.activo:
        raise HTTPException(status_code=403, detail="Usuario desactivado")

    token = create_access_token({
        "sub": usuario.id,
        "taller_id": usuario.taller_id,
        "rol": usuario.rol,
    })
    return TokenResponse(access_token=token, usuario=UsuarioOut.model_validate(usuario))


@router.get("/me", response_model=UsuarioOut)
def me(current_user=Depends(get_current_user)):
    return current_user
